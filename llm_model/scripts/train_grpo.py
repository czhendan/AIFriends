"""阶段2: GRPO 训练 —— 在 SFT 模型上用 GRPO 优化回复质量。"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # llm_model/

import json
import time
import yaml
import torch

# 补丁: trl 需要 FSDPModule，torch 2.5 已移除
import torch.distributed.fsdp as _fsdp
if not hasattr(_fsdp, "FSDPModule"):
    from torch.distributed.fsdp import FullyShardedDataParallel
    _fsdp.FSDPModule = FullyShardedDataParallel

# 注意: transformers 必须在 datasets 之前导入，否则 Windows 下会 segfault
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from datasets import Dataset
from peft import LoraConfig, PeftModel
from trl import GRPOConfig, GRPOTrainer
from reward.reward_model import compute_rewards

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


def train_grpo():
    # 确保 CUDA 可用
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA 不可用，GRPO 训练需要 GPU")
    torch.backends.cudnn.benchmark = True
    torch.cuda.empty_cache()
    print(f"GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB)")

    config = load_config()
    model_cfg = config["model"]
    qlora_cfg = config["qlora"]
    grpo_cfg = config["grpo"]
    output_cfg = config["output"]
    reward_cfg = config["reward"]

    tokenizer = AutoTokenizer.from_pretrained(model_cfg["name"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    compute_dtype = getattr(torch, qlora_cfg["bnb_4bit_compute_dtype"])
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=qlora_cfg["load_in_4bit"],
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_quant_type=qlora_cfg["bnb_4bit_quant_type"],
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        model_cfg["name"],
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=compute_dtype,
        trust_remote_code=True,
    )

    # 加载 SFT adapter，merge 后重新加 LoRA 供 GRPO 训练
    sft_path = _resolve(output_cfg["sft_adapter"])
    model = PeftModel.from_pretrained(base_model, sft_path)
    model = model.merge_and_unload()
    # merge_and_unload 后 model 在 CPU，需要移到 CUDA
    model = model.to("cuda")

    lora_config = LoraConfig(
        r=qlora_cfg["lora_r"],
        lora_alpha=qlora_cfg["lora_alpha"],
        lora_dropout=qlora_cfg["lora_dropout"],
        target_modules=qlora_cfg["lora_target_modules"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    # 不在此处调用 get_peft_model，GRPOTrainer 会通过 peft_config 自行管理 LoRA

    # 加载数据集（只需要 prompt 部分）
    dataset_path = os.path.join(PROJECT_DIR, "data", "dataset.jsonl")
    prompts = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            user_msgs = [m["content"] for m in item["messages"] if m["role"] == "user"]
            if user_msgs:
                prompts.append({"prompt": user_msgs[0]})
    dataset = Dataset.from_list(prompts)

    # Reward 包装
    reward_weights = {
        "length": reward_cfg["length_weight"],
        "diversity": reward_cfg["diversity_weight"],
        "anti_pattern": reward_cfg["anti_pattern_weight"],
        "completeness": reward_cfg["completeness_weight"],
    }

    def reward_func(prompts=None, completions=None, completion_ids=None, **kwargs) -> list[float]:
        texts = []
        for c in completions:
            if isinstance(c, str):
                texts.append(c)
            elif isinstance(c, list) and c:
                texts.append(c[0].get("content", ""))
            else:
                texts.append("")
        return compute_rewards(texts, reward_weights)

    grpo_output_dir = _resolve(output_cfg["grpo_adapter"])
    grpo_training_args = GRPOConfig(
        output_dir=grpo_output_dir,
        per_device_train_batch_size=grpo_cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=grpo_cfg["gradient_accumulation_steps"],
        learning_rate=grpo_cfg["learning_rate"],
        num_train_epochs=grpo_cfg["num_train_epochs"],
        num_generations=grpo_cfg["num_generations"],
        max_completion_length=grpo_cfg["max_completion_length"],
        beta=grpo_cfg["beta"],
        bf16=True,
        optim="paged_adamw_8bit",
        report_to="none",
        logging_steps=5,
    )

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=reward_func,
        args=grpo_training_args,
        train_dataset=dataset,
        peft_config=lora_config,
    )

    # 重置峰值显存统计，记录开始时间
    torch.cuda.reset_peak_memory_stats()
    start_time = time.time()

    print(f"Starting GRPO training on {len(dataset)} prompts...")
    trainer.train()

    # 收集训练统计
    end_time = time.time()
    total_seconds = end_time - start_time
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    peak_vram = torch.cuda.max_memory_allocated() / 1024**3
    current_vram = torch.cuda.memory_allocated() / 1024**3

    print(f"\n{'='*50}")
    print(f"GRPO 训练完成")
    print(f"{'='*50}")
    print(f"总耗时:       {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    print(f"峰值显存:     {peak_vram:.2f} GB")
    print(f"当前显存:     {current_vram:.2f} GB")
    print(f"GPU 总显存:   {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"{'='*50}")

    trainer.save_model(grpo_output_dir)
    tokenizer.save_pretrained(grpo_output_dir)
    print(f"\nGRPO adapter saved to {grpo_output_dir}")


if __name__ == "__main__":
    train_grpo()
