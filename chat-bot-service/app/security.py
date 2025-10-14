import re
import math
from typing import Dict, List

ENTROPY_TOKEN_THRESHOLD = 4.0

INJECTION_PATTERNS = [
    re.compile(r"(?i)\\bignore (all )?instructions\\b"),
    re.compile(r"(?i)\\bignore previous\\b|\\bdisregard previous\\b"),
    re.compile(r'(?i)\\boutput\\s*:\\s*["\']?.+["\']?'),
]

SECRET_PATTERNS = [
    re.compile(
        r'(?i)(password|pass|pwd|secret|token|api[_-]?key)\\s*[:=]\\s*["\']?[\\S]{4,}["\']?'
    ),
    re.compile(r"-----BEGIN .*PRIVATE KEY-----"),
    re.compile(r'(?i)root\\s*[:=]\\s*["\']?[\\S]{3,}["\']?'),
]


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    H = 0.0
    n = len(s)
    for v in freq.values():
        p = v / n
        H -= p * math.log2(p)
    return H


def looks_like_secret(text: str) -> bool:
    for p in SECRET_PATTERNS:
        if p.search(text):
            return True
    tokens = re.findall(r"[A-Za-z0-9\-_]{8,}", text)
    for t in tokens:
        if shannon_entropy(t) > ENTROPY_TOKEN_THRESHOLD:
            return True
    return False


def contains_injection(text: str) -> bool:
    for p in INJECTION_PATTERNS:
        if p.search(text):
            return True
    return False


def ingestion_filter(chunk_text: str) -> Dict:
    report = {"text": chunk_text, "action": "keep", "reasons": []}
    if contains_injection(chunk_text):
        report["action"] = "sanitize"
        report["reasons"].append("prompt_injection")
        for p in INJECTION_PATTERNS:
            chunk_text = p.sub("[REMOVED_INJECTION]", chunk_text)
        report["text"] = chunk_text
    if looks_like_secret(chunk_text):
        report["action"] = "quarantine"
        report["reasons"].append("secret_detected")
    return report


def sanitize_for_runtime(retrieved_chunks: List[Dict]) -> List[Dict]:
    safe_chunks = []
    for ch in retrieved_chunks:
        text = ch.get("chunk", "")
        report = ingestion_filter(text)
        if report["action"] == "quarantine" or report["action"] == "sanitize":
            continue
        if looks_like_secret(text):
            text = re.sub(r"([A-Za-z0-9\-_]{8,})", "[REDACTED]", text)
            ch["chunk"] = text
            ch["meta"] = ch.get("meta", {})
            ch["meta"]["redacted_runtime"] = True
        safe_chunks.append(ch)
    return safe_chunks
