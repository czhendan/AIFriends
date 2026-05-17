"""纯规则 reward 函数，用于 GRPO 训练阶段。"""
import re


ANTI_PATTERNS = [
    r"作为.{0,5}(AI|人工智能|语言模型|助手)",
    r"我只是.{0,5}(模型|AI|程序)",
    r"无法.{0,5}(回答|理解|处理)",
    r"抱歉.{0,5}(无法|不能)",
    r"请咨询",
    r"建议您",
]


def score_length(text: str, min_len: int = 15, max_len: int = 512) -> float:
    """长度合理性：过短 0 分，范围内满分，过长递减。"""
    length = len(text)
    if length < min_len:
        return 0.0
    if length <= max_len:
        return 1.0
    return max(0.0, 2.0 - length / max_len)


def score_diversity(text: str) -> float:
    """词汇多样性：唯一词数/总词数，过短回复按比例惩罚。"""
    words = text.strip().split()
    if not words:
        return 0.0
    if len(words) < 5:
        return (len(set(words)) / len(words)) * (len(words) / 5)
    return len(set(words)) / len(words)


def score_anti_pattern(text: str) -> float:
    """反模式检测：命中出戏词则 0 分，否则满分。"""
    for pattern in ANTI_PATTERNS:
        if re.search(pattern, text):
            return 0.0
    return 1.0


def score_completeness(text: str) -> float:
    """完整性：是否以完整标点结束、无截断、非空。"""
    if not text or not text.strip():
        return 0.0
    text = text.strip()
    if text.endswith((".", "。", "!", "！", "?", "？", "~", "…", "”", "“")):
        return 1.0
    if text.endswith((",", "，", "、", "：", ":")):
        return 0.5
    return 0.8


def compute_reward(completion: str, weights: dict = None) -> float:
    """计算单条回复的总 reward。

    反模式命中时直接返回 0（硬惩罚），其余维度加权求和。
    """
    if weights is None:
        weights = {
            "length": 0.25,
            "diversity": 0.25,
            "anti_pattern": 0.25,
            "completeness": 0.25,
        }

    anti_pattern_score = score_anti_pattern(completion)
    if anti_pattern_score == 0.0:
        return 0.0

    scores = {
        "length": score_length(completion),
        "diversity": score_diversity(completion),
        "completeness": score_completeness(completion),
    }
    total = (
        scores["length"] * weights["length"]
        + scores["diversity"] * weights["diversity"]
        + scores["completeness"] * weights["completeness"]
    )
    return total


def compute_rewards(completions: list[str], weights: dict = None) -> list[float]:
    """批量计算 reward。"""
    return [compute_reward(c, weights) for c in completions]
