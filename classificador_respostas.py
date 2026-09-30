from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

@dataclass(frozen=True)
class Classification:
    status: str
    confidence: float
    reason: str

POSITIVE_TERMS = (
    "devolvido",
    "devolucao realizada",
    "produto retornou",
    "recebemos a devolucao",
    "item recebido",
)

NEGATIVE_TERMS = (
    "nao devolvido",
    "nao recebemos",
    "cliente nao devolveu",
    "sem retorno",
    "aguardando devolucao",
)

def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", value).strip()

def classify_reply(subject: str, body: str) -> Classification:
    text = normalize(f"{subject} {body}")

    negative = [term for term in NEGATIVE_TERMS if term in text]
    positive = [term for term in POSITIVE_TERMS if term in text]

    if negative:
        return Classification("PENDING", min(0.95, 0.60 + len(negative) * 0.1), f"Negative/pending terms: {', '.join(negative)}")
    if positive:
        return Classification("RETURNED", min(0.95, 0.60 + len(positive) * 0.1), f"Positive return terms: {', '.join(positive)}")
    return Classification("REVIEW", 0.35, "No conclusive rule matched.")
