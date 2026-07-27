"""Conservative, local keyword classifier for routing high-risk messages."""
from __future__ import annotations

from enum import StrEnum


class Intent(StrEnum):
    GENERAL_CHAT = "GENERAL_CHAT"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    SUICIDE = "SUICIDE"
    THERAPIST_SEARCH = "THERAPIST_SEARCH"


SUICIDE_TERMS = ("suicide", "kill myself", "end my life", "want to die", "self harm", "self-harm", "hurt myself", "cut myself")
THERAPIST_TERMS = ("therapist", "counsellor", "counselor", "psychologist", "psychiatrist", "nearby therapy")
MENTAL_HEALTH_TERMS = ("anxiety", "depression", "panic", "mental health", "stress", "trauma", "ptsd", "insomnia", "grief", "sad", "overwhelmed")


def classify_intent(message: str) -> Intent:
    text = message.casefold()
    if any(term in text for term in SUICIDE_TERMS):
        return Intent.SUICIDE
    if any(term in text for term in THERAPIST_TERMS):
        return Intent.THERAPIST_SEARCH
    if any(term in text for term in MENTAL_HEALTH_TERMS):
        return Intent.MENTAL_HEALTH
    return Intent.GENERAL_CHAT
