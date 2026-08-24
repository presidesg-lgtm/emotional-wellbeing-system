import re


class RiskSupportService:
    """
    Provide a non-diagnostic, rule-based safety-support layer.

    This service does not attempt to diagnose a mental-health
    condition. It looks for a limited set of concerning language
    patterns so that the interface can provide stronger supportive
    guidance when appropriate.
    """

    IMMEDIATE_PATTERNS = (
        r"\bkill myself\b",
        r"\bend my life\b",
        r"\btake my own life\b",
        r"\bcommit suicide\b",
        r"\bsuicid(?:e|al)\b",
        r"\bhurt myself\b",
        r"\bharm myself\b",
        r"\bself[- ]?harm\b",
        r"\bdon'?t want to live\b",
        r"\bdo not want to live\b",
        r"\bwant to die\b",
        r"\bwish i were dead\b",
        r"\bwish i was dead\b",
        r"\bbetter off dead\b",
        r"\bno reason to live\b",
    )

    ELEVATED_PATTERNS = (
        r"\blife is pointless\b",
        r"\blife feels pointless\b",
        r"\bnothing matters\b",
        r"\bno hope\b",
        r"\bhopeless\b",
        r"\bcan'?t go on\b",
        r"\bcannot go on\b",
        r"\bno way out\b",
        r"\beveryone would be better without me\b",
        r"\bpeople would be better without me\b",
        r"\bi am a burden\b",
        r"\bi'?m a burden\b",
        r"\bcompletely alone\b",
    )

    def assess_text(self, text: str) -> dict:
        """
        Return a support level and user-facing safety message.

        The result is intentionally framed as an automated support
        check, not a clinical risk score or diagnosis.
        """

        cleaned_text = " ".join(text.strip().lower().split())

        if self._matches_any(
            cleaned_text,
            self.IMMEDIATE_PATTERNS,
        ):
            return {
                "level": "immediate",
                "title": "Immediate support encouraged",
                "message": (
                    "Some of the language you entered suggests that "
                    "you may need immediate real-world support. "
                    "Please consider moving to a safer place, staying "
                    "with someone you trust, and contacting local "
                    "emergency services or a crisis-support service "
                    "in your area if you may be in immediate danger. "
                    "This automated message is supportive guidance, "
                    "not a clinical assessment."
                ),
            }

        if self._matches_any(
            cleaned_text,
            self.ELEVATED_PATTERNS,
        ):
            return {
                "level": "elevated",
                "title": "Additional support may be helpful",
                "message": (
                    "Your wording contains signs of significant "
                    "distress. Consider reaching out to someone you "
                    "trust or arranging support from a qualified "
                    "counsellor or other appropriate professional. "
                    "If you begin to feel that you may be in immediate "
                    "danger, seek urgent real-world help. This "
                    "automated message is not a diagnosis."
                ),
            }

        return {
            "level": "standard",
            "title": "Supportive reflection",
            "message": None,
        }

    @staticmethod
    def _matches_any(
        text: str,
        patterns: tuple[str, ...],
    ) -> bool:
        """
        Return True when any configured phrase pattern matches.
        """

        return any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for pattern in patterns
        )
