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
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]

    def check(self, text: str) -> tuple[bool, Optional[str]]:
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
        text = re.sub(r"[-]{3,}", "", text)
        text = re.sub(r"[=]{3,}", "", text)
        text = text.replace("{{", "{ {").replace("}}", "} }")
        return text.strip()


class PIIDetector:
    """
    Detect and mask personally identifiable information.
    Works on BOTH input (before llm) and output (before client)
    """

    PATTERNS = {
        # =====================================================
        # Contact Information
        # =====================================================
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "phone": re.compile(
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
        ),
        # =====================================================
        # Government IDs
        # =====================================================
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "passport": re.compile(r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b"),
        # =====================================================
        # Financial
        # =====================================================
        "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
        # =====================================================
        # Authentication / Secrets
        # =====================================================
        "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
        "bearer_token": re.compile(
            r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
            re.IGNORECASE,
        ),
        "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
        "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]+\b"),
        "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
        "google_api_key": re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
        # =====================================================
        # AWS
        # =====================================================
        "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "aws_secret_key": re.compile(r"\b[A-Za-z0-9/+=]{40}\b"),
        # =====================================================
        # Database Connection Strings
        # =====================================================
        "postgres_url": re.compile(r"postgres(?:ql)?://[^\s]+"),
        "mongodb_url": re.compile(r"mongodb(?:\+srv)?://[^\s]+"),
        "redis_url": re.compile(r"redis://[^\s]+"),
        # =====================================================
        # Private Keys / Certificates
        # =====================================================
        "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "certificate": re.compile(r"-----BEGIN CERTIFICATE-----"),
        # =====================================================
        # Network
        # =====================================================
        "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "ipv6": re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"),
        "mac_address": re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"),
        # =====================================================
        # URLs
        # =====================================================
        "url": re.compile(r"https?://[^\s]+"),
        # =====================================================
        # Cryptocurrency
        # =====================================================
        "bitcoin_wallet": re.compile(r"\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b"),
        "ethereum_wallet": re.compile(r"\b0x[a-fA-F0-9]{40}\b"),
    }

    MASK_MAP = {
        "email": "[EMAIL REDACTED]",
        "phone": "[PHONE REDACTED]",
        "ssn": "[SSN REDACTED]",
        "passport": "[PASSPORT REDACTED]",
        "credit_card": "[CARD REDACTED]",
        "iban": "[IBAN REDACTED]",
        "jwt": "[JWT REDACTED]",
        "bearer_token": "[BEARER TOKEN REDACTED]",
        "github_token": "[GITHUB TOKEN REDACTED]",
        "slack_token": "[SLACK TOKEN REDACTED]",
        "openai_key": "[OPENAI KEY REDACTED]",
        "google_api_key": "[GOOGLE API KEY REDACTED]",
        "aws_access_key": "[AWS ACCESS KEY REDACTED]",
        "aws_secret_key": "[AWS SECRET KEY REDACTED]",
        "postgres_url": "[POSTGRES URL REDACTED]",
        "mongodb_url": "[MONGODB URL REDACTED]",
        "redis_url": "[REDIS URL REDACTED]",
        "private_key": "[PRIVATE KEY REDACTED]",
        "certificate": "[CERTIFICATE REDACTED]",
        "ipv4": "[IP REDACTED]",
        "ipv6": "[IP REDACTED]",
        "mac_address": "[MAC ADDRESS REDACTED]",
        "url": "[URL REDACTED]",
        "bitcoin_wallet": "[BITCOIN WALLET REDACTED]",
        "ethereum_wallet": "[ETHEREUM WALLET REDACTED]",
    }

    def detect(self, text: str) -> dict[str, list[str]]:
        """Detect PII types present in test."""
        found = {}

        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                found[pii_type] = matches
        return found

    def mask(self, text: str) -> str:
        """Relplace all PII with redaction markers."""
        masked = text
        for pii_type, pattern in self.PATTERNS.items():
            masked = pattern.sub(self.MASK_MAP[pii_type], masked)
        return masked


class OutputValidator:
    """
    Validate LLM output before returning to the client.
    Catches PII leakage and harmfull content in response.
    """

    HARMFUL_PATTERNS = [
        re.compile(r"here('s| is) (how|the way) to (hack|steal|attack)", re.I),
        re.compile(r"password\s+is\s+", re.I),
        re.compile(r"api[_\s]?key\s*[:=]", re.I),
    ]

    def __init__(self):
        self.pii_detector = PIIDetector()

    def validate(self, output: str) -> tuple[str, list[str]]:
        """
        Validate and clean output
        Returns: (cleaned_output, list_of_warning)
        """

        warning = []

        # Check for PII leakage in output
        pii_found = self.pii_detector.detect(output)
        if pii_found:
            output = self.pii_detector.mask(output)
            warning.append(f"PII masked in output: {list(pii_found.keys())}")

        # Check for harmful content

        for pattern in self.HARMFUL_PATTERNS:
            if pattern.search(output):
                output = "[Response Blocked: potentially harmfull content]"
                warning.append("Harmfull content blocked")
                break

        return output, warning


class SecurityPipeline:
    """
    Full security Pipeline that processes input and output.
    This is single class you wire into your API.
    """

    def __init__(self):
        self.sanitizer = InputSanitization()
        self.pii_detector = PIIDetector()
        self.output_validator = OutputValidator()

    @traceable(name="security_check_input")
    def check_input(self, text: str) -> tuple[bool, str, list[str]]:
        """
        Process input through security checks.
        Returns. (is_allowed, cleaned_text, security_notes)
        """

        notes = []

        # Setp-1: Check for injection

        is_safe, reason = self.sanitizer.check(text)
        if not is_safe:
            return False, "", [reason]

        # Step-2: Clean input

        cleaned = self.sanitizer.clean(text)

        # Step-3: Mask PII before it reaches the LLM

        pii_found = self.pii_detector.detect(cleaned)

        if pii_found:
            cleaned = self.pii_detector.mask(cleaned)
            notes.append(f"Input PII masked: {list(pii_found.keys())}")

        return True, cleaned, notes

    @traceable(name="security_check_output")
    def check_output(self, text: str) -> tuple[str, list[str]]:
        """
        Validate output befor returning it to the client
        Returns: (cleaned_output, warning)
        """

        return self.output_validator.validate(text)
