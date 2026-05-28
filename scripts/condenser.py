#!/usr/bin/env python3
"""Bilingual text condenser — removes meta/transition filler, keeps core semantics."""

from __future__ import annotations

import functools
import json
import re
from collections import Counter
from itertools import combinations

import spacy


class BilingualCondenser:
    """Compress Chinese/English text while preserving keywords and core meaning."""

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        enable_duplicate_filter: bool = True,
        custom_explanation_markers: list[str] | None = None,
        strength: str = "balanced",
        lazy_load: bool = True,
    ):
        self.similarity_threshold = similarity_threshold
        self.enable_duplicate_filter = enable_duplicate_filter
        self.strength = strength
        self._nlp_zh = None
        self._nlp_en = None
        self._lazy_load = lazy_load

        if not lazy_load:
            self._load_models()

        self._compile_patterns()
        self._init_blacklists(custom_explanation_markers)

    @property
    def nlp_zh(self):
        if self._nlp_zh is None:
            self._load_models()
        return self._nlp_zh

    @property
    def nlp_en(self):
        if self._nlp_en is None:
            self._load_models()
        return self._nlp_en

    def _load_models(self):
        self._nlp_zh = spacy.load("zh_core_web_sm", disable=["ner", "textcat", "lemmatizer"])
        self._nlp_en = spacy.load("en_core_web_sm", disable=["ner", "textcat", "lemmatizer"])

    def _init_blacklists(self, custom_markers: list[str] | None):
        self.blacklist_zh = {
            "meta": ["让我", "我来", "我需要", "我应该", "我得", "我要", "首先我", "接下来我"],
            "transition": [
                "首先", "其次", "然后", "接下来", "因此", "所以", "综上所述",
                "总而言之", "简言之", "由此可见",
            ],
            "hesitation": [
                "可能", "大概", "也许", "或许", "我认为", "我觉得",
                "个人认为", "据我所知", "一般来说",
            ],
            "explanation": ["也就是说", "换句话说", "这意味着", "简单来说", "即", "就是说", "换言之"],
        }
        self.blacklist_en = {
            "meta": [
                "Let me", "I will", "I need to", "I should", "I have to",
                "Okay", "Alright", "Sure", "No problem", "Thank you",
            ],
            "transition": [
                "First", "Second", "Third", "Then", "Next", "Therefore", "So",
                "Thus", "Hence", "Consequently", "In summary", "In conclusion",
            ],
            "hesitation": [
                "maybe", "probably", "perhaps", "I think", "I believe",
                "in my opinion", "as far as I know", "generally speaking",
            ],
            "explanation": ["that is", "in other words", "which means", "simply put", "i.e.", "e.g."],
        }

        if self.strength == "aggressive":
            self.blacklist_zh["meta"].extend(["好的", "没问题", "很高兴为您", "希望对您有帮助", "谢谢"])
            self.blacklist_en["meta"].extend(["Okay", "Alright", "Sure", "No problem", "Thank you"])

        if custom_markers:
            self.blacklist_zh["explanation"].extend(
                m for m in custom_markers if re.search(r"[\u4e00-\u9fff]", m)
            )
            self.blacklist_en["explanation"].extend(
                m for m in custom_markers if not re.search(r"[\u4e00-\u9fff]", m)
            )

        self._blacklist_pattern_zh = self._build_blacklist_pattern(self.blacklist_zh, "zh")
        self._blacklist_pattern_en = self._build_blacklist_pattern(self.blacklist_en, "en")

    def _build_blacklist_pattern(self, blacklist: dict[str, list[str]], lang: str) -> re.Pattern:
        all_phrases: list[str] = []
        for cat_phrases in blacklist.values():
            all_phrases.extend(cat_phrases)
        all_phrases.sort(key=len, reverse=True)
        if not all_phrases:
            return re.compile(r"(?!.*)")

        escaped = "|".join(map(re.escape, all_phrases))
        if lang == "en":
            return re.compile(r"\b(?:" + escaped + r")\b", re.I)
        return re.compile(r"(?:^|[^一-龥])(?:" + escaped + r")(?:[^一-龥]|$)", re.I)

    def _compile_patterns(self):
        self.meta_zh = re.compile(
            r"(?:让我(?:[^。！？\n]{0,20}?)(?:思考|理解|分析|回答|解决|处理|介绍|说明)"
            r"(?:[^。！？\n]{0,5}?)[：。，])",
            flags=re.I,
        )
        self.meta_en = re.compile(
            r"(?:Let me(?:[^.!?\n]{0,30}?)(?:think|understand|analyze|answer|solve|explain|describe)"
            r"(?:[^.!?\n]{0,5}?)[:.,])",
            flags=re.I,
        )
        self.trans_zh = re.compile(
            r"^(?:首先|其次|然后|接下来|因此|所以|综上所述|总而言之)[，：]?\s*",
            flags=re.M,
        )
        self.trans_en = re.compile(
            r"^(?:First|Second|Third|Then|Next|Therefore|So|Thus|Hence)[,:]?\s*",
            flags=re.M | re.I,
        )
        self.whitespace = re.compile(r"\s+")
        self.url_pattern = re.compile(r"https?://\S+|www\.\S+")
        self.email_pattern = re.compile(r"\S+@\S+\.\S+")

    @functools.lru_cache(maxsize=1000)
    def _detect_language(self, text: str) -> str:
        return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"

    def condense(self, text: str, return_stats: bool = False):
        if not text or len(text.strip()) < 10:
            stripped = text.strip()
            return (stripped, {}) if return_stats else stripped

        original_length = len(text)
        text = self._preprocess_text(text)
        text = self._fast_semantic_filter(text)
        if not text:
            return ("", {}) if return_stats else ""

        text = self._syntactic_compress(text)
        if not text:
            return ("", {}) if return_stats else ""

        text = self._statistical_filter(text)
        text = self._post_process(text)

        if self.enable_duplicate_filter:
            text = self._duplicate_filter(text)
            text = self._post_process(text)

        if return_stats:
            stats = {
                "original_length": original_length,
                "compressed_length": len(text),
                "compression_ratio": round(1 - len(text) / original_length if original_length else 0, 2),
            }
            return text, stats
        return text

    def condense_batch(self, texts: list[str]) -> list[str]:
        return [self.condense(text) for text in texts]

    def _preprocess_text(self, text: str) -> str:
        text = self.url_pattern.sub(" [URL] ", text)
        text = self.email_pattern.sub(" [EMAIL] ", text)
        return text

    def _fast_semantic_filter(self, text: str) -> str:
        text = self.meta_zh.sub("", text)
        text = self.meta_en.sub("", text)
        text = self.trans_zh.sub("", text)
        text = self.trans_en.sub("", text)

        lang = self._detect_language(text)
        if lang == "zh":
            text = self._blacklist_pattern_zh.sub("", text)
        else:
            text = self._blacklist_pattern_en.sub("", text)

        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    def _syntactic_compress(self, text: str) -> str:
        lang = self._detect_language(text)
        nlp = self.nlp_zh if lang == "zh" else self.nlp_en
        doc = nlp(text)

        if self.strength == "light":
            core_deps = {"nsubj", "ROOT", "dobj", "attr", "pobj", "amod", "advmod", "nmod", "compound"}
        elif self.strength == "aggressive":
            core_deps = {"nsubj", "ROOT", "dobj"}
        else:
            core_deps = {"nsubj", "ROOT", "dobj", "attr", "pobj", "amod", "nmod"}

        essential_stops = {
            "zh": {"有", "是", "在", "用", "能", "会", "把", "被", "不", "没", "未"},
            "en": {"is", "are", "be", "been", "being", "have", "has", "had", "can", "could", "will", "would", "not", "no"},
        }

        compressed: list[str] = []
        for sent in doc.sents:
            tokens: list[str] = []
            for token in sent:
                if (
                    token.dep_ in core_deps
                    or token.pos_ in {"NOUN", "VERB", "NUM", "PROPN", "ADJ"}
                    or token.text.lower() in essential_stops[lang]
                ):
                    tokens.append(token.text)

            if tokens:
                if lang == "zh":
                    compressed.append("".join(tokens))
                else:
                    compressed.append(" ".join(tokens))

        if not compressed:
            return ""

        sep = "。" if lang == "zh" else ". "
        return sep.join(compressed) + ("。" if lang == "zh" else ".")

    def _statistical_filter(self, text: str) -> str:
        lang = self._detect_language(text)
        if lang == "zh":
            chars = list(text)
            if len(chars) < 6:
                return text

            freq = Counter(c for c in chars if c.strip() and c not in "。，！？、")
            threshold = max(0.2 * len(chars), 3)
            filtered = [c for c in chars if not c.strip() or c in "。，！？、" or freq[c] < threshold]
            return "".join(filtered)

        words = [token.text for token in self.nlp_en(text) if token.text.strip()]
        if len(words) < 4:
            return text

        freq = Counter(w.lower() for w in words)
        threshold = max(0.15 * len(words), 2)
        filtered = [w for w in words if freq[w.lower()] < threshold]
        return " ".join(filtered)

    def _post_process(self, text: str) -> str:
        lang = self._detect_language(text)
        if lang == "zh":
            text = re.sub(r"[。！？]+", "。", text)
            text = re.sub(r"[，、]+", "，", text)
            text = re.sub(r"，{2,}", "，", text)
            text = re.sub(r"。{2,}", "。", text)
            text = re.sub(r"，。", "。", text)
        else:
            text = re.sub(r"[.!?]+", ".", text)
            text = re.sub(r"[,;]+", ",", text)
            text = re.sub(r",{2,}", ",", text)
            text = re.sub(r"\.{2,}", ".", text)
            text = re.sub(r",\.", ".", text)

        text = self.whitespace.sub(" ", text)
        return text.strip("，。！？：；,.!?;: ")

    def _duplicate_filter(self, text: str) -> str:
        lang = self._detect_language(text)
        nlp = self.nlp_zh if lang == "zh" else self.nlp_en
        doc = nlp(text)
        sentences = [sent for sent in doc.sents if len(sent.text.strip()) > 5]
        if len(sentences) < 2:
            return text

        keep = [True] * len(sentences)
        if lang == "zh":
            sets = [set(sent.text.replace(" ", "")) for sent in sentences]
        else:
            sets = [set(t.text.lower() for t in sent if not t.is_punct) for sent in sentences]

        for i, j in combinations(range(len(sentences)), 2):
            if not keep[i] or not keep[j]:
                continue

            len_i, len_j = len(sentences[i].text), len(sentences[j].text)
            if abs(len_i - len_j) > 0.5 * max(len_i, len_j, 1):
                continue

            inter = len(sets[i] & sets[j])
            union = len(sets[i] | sets[j])
            jaccard = inter / union if union else 0

            jaccard_threshold = 0.5 if lang == "zh" else 0.3
            if jaccard < jaccard_threshold:
                continue

            sim = sentences[i].similarity(sentences[j])
            if sim > self.similarity_threshold:
                keep[j] = False
                continue
            if sim > 0.95 and min(len_i, len_j) < 15:
                keep[j] = False

        filtered = [sentences[i].text for i, keep_flag in enumerate(keep) if keep_flag]
        if not filtered:
            return text

        return ("。" if lang == "zh" else ". ").join(filtered) + ("。" if lang == "zh" else ".")

    def save_config(self, filepath: str):
        config = {
            "similarity_threshold": self.similarity_threshold,
            "enable_duplicate_filter": self.enable_duplicate_filter,
            "strength": self.strength,
            "lazy_load": self._lazy_load,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_config(cls, filepath: str):
        with open(filepath, encoding="utf-8") as f:
            config = json.load(f)
        return cls(**config)
