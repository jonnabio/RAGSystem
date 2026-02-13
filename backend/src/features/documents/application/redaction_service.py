
import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

class RedactionService:
    """
    Service for identifying and redacting PII from text.
    """

    # Patterns for PII detection
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b(?:\d[ -]*?){13,16}\b'
    }

    def redact_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Redact PII from text.
        Returns tuple of (redacted_text, list_of_redacted_types).
        """
        redacted_text = text
        redactions = set()

        for pii_type, pattern in self.PATTERNS.items():
            regex = re.compile(pattern)
            if regex.search(redacted_text):
                # Replace with [REDACTED: TYPE]
                redacted_text = regex.sub(f"[REDACTED: {pii_type.upper()}]", redacted_text)
                redactions.add(pii_type)

        if redactions:
            logger.info(f"Redacted {len(redactions)} PII types: {', '.join(redactions)}")

        return redacted_text, list(redactions)
