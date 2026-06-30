"""
Security Layer
Input sanitization, PII detection/masking, output validation.
"""

import re
from typing import Optional
from langsmith import traceable

# === Input Sanitiation ===


class InputSanitization:
    """
    Sanitize the user input before it reaches the LLM.
    Detect prompt injection patterns and clean dangerous content
    """

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(all\s+)?previous",
        r"new\s+instructions\s*:",
        r"system\s*prompt",
        r"---\s*end\s*(of)?\s*prompt",
        r"pretend\s+you\s+are",
        r"act\s+as\s+(if\s+)?you",
        r"bypass\s+(all\s+)?restrictions",
        r"reveal\s+(your|the)\s+(system|instructions|prompt)",
        r"you\s+are\s+now\s+(DAN|jailbroken)",
    ]

    def __init__(self):
        self.patterns = [
            re.compile(p, re.IGNORECASE)
            for p in self.INJECTION_PATTERNS
        ]

    def check(self, text: str)-> tuple[bool, Optional[str]]:
        """
        Check if the input is safe.
        Return : (is_safe, rejection_reason)
        """

        for pattern in self.patterns:
            if pattern.search(text):
                return False, "Blocked: potential prompt injection detection"
        return True, None

    def clean(self, text: str) -> str:
        """Remove potentially dangerous delimiters from inputs."""
        text = re.sub(r'[-]{3,}', '', text)
        text = re.sub(r'[=]{3,}', '', text)
        text = text.replace('{{', '{ {').replace('}}', '} }')
        return text.strip()



class PIIDetector:
    """
    Detect and mask personally identifiable information.
    Works on BOTH input (before llm) and output (before client)
    """

    PATTERNS = {
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    }

    MASK_MAP = {
        "email": "[EMAIL REDACTED]",
        "phone": "[PHONE REDACTED]",
        "ssn": "[SSN REDACTED]",
        "credit_card": "[CARD REDACTED]",
    }


    def detect(self, text: str) -> dict[str, list[str]]:
        """Detect PII types present in test."""
        found = {}

        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                found[pii_type] = matches
        return found

    def mask(self, text:str) -> str:
        """Relplace all PII with redaction markers."""
        masked = text 
        for pii_type, pattern in self.PATTERNS.items():
            masked = pattern.sub(self.MASK_MAP[pii_type], masked)
        return masked    