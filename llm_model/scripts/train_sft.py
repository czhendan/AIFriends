"""阶段1: QLoRA SFT 训练 —— 在角色对话数据上微调基座模型。"""
import json
import os
import time
import yaml
import torch
# 注意: transformers 必须在 datasets 之前导入，否则 Windows 下会 segfault
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# llm_model/ 目录，所有相对路径以此为基准
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(path: str) -> str:
    """将 config 中的相对路径解析为绝对路径。"""
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(PROJECT_DIR, path))


def load_config() -> dict:
    config_path = os.path.join(PROJECT_DIR, "config", "train_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dataset(dataset_path: str) -> Dataset:
    data = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            data.append({"messages": item["messages"]})
    return Dataset.from_list(data)


def train_sft():
    # 确保 CUDA 可用
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA 不可用，SFT 训练需要 GPU")
    torch.backends.cudnn.benchmark = True
    torch.cuda.empty_cache()
    print(f"GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB)")

    config = load_config()
    model_cfg = config["model"]
    qlora_cfg = config["qlora"]
    sft_cfg = config["sft"]
    output_cfg = config["output"]

    tokenizer = AutoTokenizer.from_pretrained(model_cfg["name"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    compute_dtype = getattr(torch, qlora_cfg["bnb_4bit_compute_dtype"])
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=qlora_cfg["load_in_4bit"],
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_quant_type=qlora_cfg["bnb_4bit_quant_type"],
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_cfg["name"],
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=compute_dtype,
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=qlora_cfg["lora_r"],
        lora_alpha=qlora_cfg["lora_alpha"],
        lora_dropout=qlora_cfg["lora_dropout"],
        target_modules=qlora_cfg["lora_target_modules"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset_path = os.path.join(PROJECT_DIR, "data", "dataset.jsonl")
    dataset = load_dataset(dataset_path)

    def _tokenize(examples):
        texts = []
        for msgs in examples["messages"]:
            text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
            texts.append(text)
        result = tokenizer(texts, truncation=True, max_length=model_cfg["max_seq_length"], padding="max_length")
        result["labels"] = result["input_ids"].copy()
        return result

    tokenized_dataset = dataset.map(_tokenize, batched=True, remove_columns=dataset.column_names)

    training_args = TrainingArguments(
        output_dir=_resolve(output_cfg["sft_adapter"]),
        per_device_train_batch_size=sft_cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=sft_cfg["gradient_accumulation_steps"],
        learning_rate=sft_cfg["learning_rate"],
        num_train_epochs=sft_cfg["num_train_epochs"],
        warmup_ratio=sft_cfg["warmup_ratio"],
        logging_steps=sft_cfg["logging_steps"],
        save_steps=sft_cfg["save_steps"],
        max_grad_norm=sft_cfg["max_grad_norm"],
        bf16=True,
        optim="paged_adamw_8bit",
        report_to="none",
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # 重置峰值显存统计，记录开始时间
    torch.cuda.reset_peak_memory_stats()
    start_time = time.time()

    print(f"Starting SFT training on {len(dataset)} samples...")
    trainer.train()

    # 收集训练统计
    end_time = time.time()
    total_seconds = end_time - start_time
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    peak_vram = torch.cuda.max_memory_allocated() / 1024**3
    current_vram = torch.cuda.memory_allocated() / 1024**3

    print(f"\n{'='*50}")
    print(f"SFT 训练完成")
    print(f"{'='*50}")
    print(f"总耗时:       {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    print(f"峰值显存:     {peak_vram:.2f} GB")
    print(f"当前显存:     {current_vram:.2f} GB")
    print(f"GPU 总显存:   {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"{'='*50}")

    sft_path = _resolve(output_cfg["sft_adapter"])
    model.save_pretrained(sft_path)
    tokenizer.save_pretrained(sft_path)

    # 将 checkpoint 中的 adapter 文件提升到上级目录，方便后续脚本直接读取
    checkpoints = sorted(
        d for d in os.listdir(sft_path) if d.startswith("checkpoint-")
    )
    if checkpoints:
        import shutil
        ckpt_dir = os.path.join(sft_path, checkpoints[-1])
        for fname in os.listdir(ckpt_dir):
            src = os.path.join(ckpt_dir, fname)
            dst = os.path.join(sft_path, fname)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
        print(f"已将 checkpoint/{checkpoints[-1]} 中的文件提升到 {sft_path}")
    print(f"\nSFT adapter saved to {sft_path}")


if __name__ == "__main__":
    train_sft()
