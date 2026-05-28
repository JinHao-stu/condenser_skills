"""Regex-only condenser — no spaCy dependency. Lower quality, fast startup."""

from __future__ import annotations

import re

META_ZH = re.compile(
    r"(?:让我(?:[^。！？\n]{0,20}?)(?:思考|理解|分析|回答|解决|处理|介绍|说明)(?:[^。！？\n]{0,5}?)[：。，]?|"
    r"让我(?:来|先)?(?:思考|分析|理解|看看)(?:一下)?(?:这个(?:问题|任务|情况))?[。，]?)",
    re.I,
)
META_EN = re.compile(
    r"(?:Let me(?:[^.!?\n]{0,30}?)(?:think|understand|analyze|answer|solve|explain|describe)"
    r"(?:[^.!?\n]{0,5}?)[.:,]?|Let me(?: analyze| think about)? this[.:,]?)",
    re.I,
)
TRANS_ZH = re.compile(r"^(?:首先|其次|然后|接下来|因此|所以|综上所述|总而言之)[，：]?\s*", re.M)
TRANS_EN = re.compile(r"^(?:First|Second|Third|Then|Next|Therefore|So|Thus|Hence)[,:]?\s*", re.M | re.I)
EN_META = re.compile(r"Let me\b[^.!?\n]*[.!?]\s*", re.I)

BLACKLIST_ZH = [
    "让我", "我来", "我需要", "我应该", "首先", "其次", "然后", "接下来", "因此", "所以",
    "综上所述", "总而言之", "可能", "大概", "也许", "我认为", "我觉得", "也就是说",
    "换句话说", "简单来说", "换言之",
]
BLACKLIST_EN = [
    "Let me", "I will", "I need to", "I should", "I have to", "First", "Second", "Third", "Then", "Next",
    "Therefore", "So", "Thus", "In conclusion", "maybe", "probably", "perhaps", "I think", "I believe",
    "in other words", "simply put", "that is", "which means",
]

AGGRESSIVE_ZH = ["好的", "没问题", "谢谢", "简言之", "由此可见"]
AGGRESSIVE_EN = ["Okay", "Alright", "Sure", "No problem", "Thank you", "In summary"]


def _build_pattern(phrases: list[str], lang: str) -> re.Pattern:
    phrases = sorted(set(phrases), key=len, reverse=True)
    escaped = "|".join(map(re.escape, phrases))
    if lang == "en":
        return re.compile(r"\b(?:" + escaped + r")\b", re.I)
    return re.compile(r"(?:^|[^一-龥])(?:" + escaped + r")(?:[^一-龥]|$)", re.I)


def _dedupe_lines(text: str) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for line in text.splitlines():
        key = re.sub(r"\s+", "", line.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(line.strip())
    return "\n".join(out)


def quick_condense(text: str, strength: str = "balanced") -> str:
    if not text or len(text.strip()) < 10:
        return text.strip()

    text = META_ZH.sub("", text)
    text = META_EN.sub("", text)
    text = EN_META.sub("", text)
    text = TRANS_ZH.sub("", text)
    text = TRANS_EN.sub("", text)
    text = re.sub(r"^[一下这]+(?:个?(?:问题|任务|情况))?[。，]?\s*", "", text)
    text = re.sub(r"\bthis\.\s+(?=[A-Za-z])", "", text, flags=re.I)

    zh_phrases = list(BLACKLIST_ZH)
    en_phrases = list(BLACKLIST_EN)
    if strength == "aggressive":
        zh_phrases.extend(AGGRESSIVE_ZH)
        en_phrases.extend(AGGRESSIVE_EN)

    text = _build_pattern(zh_phrases, "zh").sub("", text)
    text = _build_pattern(en_phrases, "en").sub("", text)
    text = re.sub(r"^[，,.\s]+", "", text, flags=re.M)
    text = re.sub(r"\s*,\s*", " ", text)
    text = re.sub(r"[，,]\s*[，,]+", "，", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = _dedupe_lines(text)
    text = re.sub(r"[，,]{2,}", "，", text)
    text = re.sub(r"[。.]{2,}", "。", text)
    return text.strip("，。！？：；,.!?;: \n")
