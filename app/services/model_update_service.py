import hashlib
import re
from pathlib import Path

from app.repositories.model_update_repository import (
    get_candidate_retraining_rows,
)


class ModelUpdateService:
    """
    Prepare privacy-reduced candidate data and validate local
    model directories before deployment.

    Retraining itself remains an offline ML task so a long-running
    transformer training job is never executed inside a web request.
    """

    EMAIL_PATTERN = re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        flags=re.IGNORECASE,
    )

    URL_PATTERN = re.compile(
        r"\b(?:https?://|www\.)\S+\b",
        flags=re.IGNORECASE,
    )

    PHONE_PATTERN = re.compile(
        r"(?<!\w)(?:\+?\d[\d\s().-]{6,}\d)(?!\w)"
    )

    HANDLE_PATTERN = re.compile(
        r"(?<!\w)@[A-Za-z0-9_]{2,}"
    )

    def __init__(self):
        self.project_root = (
            Path(__file__).resolve().parents[2]
        )

        self.saved_models_root = (
            self.project_root
            / "ml"
            / "saved_models"
        ).resolve()

    def build_anonymized_candidate_rows(self):
        """
        Return a de-identified candidate export.

        The export excludes account identifiers and masks common
        direct identifiers that may appear inside free text.
        """

        source_rows = get_candidate_retraining_rows()

        export_rows = []

        for row in source_rows:
            anonymous_id = hashlib.sha256(
                (
                    "wellbeing-retraining-record:"
                    f"{row['source_record_id']}"
                ).encode("utf-8")
            ).hexdigest()[:16]

            export_rows.append(
                {
                    "anonymous_record_id": anonymous_id,
                    "text": self._redact_text(
                        row["submitted_text"]
                    ),
                    "current_prediction": row[
                        "predicted_emotion"
                    ],
                    "confidence": float(
                        row["confidence"]
                    ),
                    "recorded_date": (
                        row["created_at"].date().isoformat()
                    ),
                }
            )

        return export_rows

    def validate_model_directory(
        self,
        directory_name: str,
    ):
        """
        Validate a candidate Hugging Face model directory.

        Only folders inside ml/saved_models are accepted.
        """

        cleaned_name = directory_name.strip()

        if not cleaned_name:
            return (
                False,
                "Model directory is required.",
            )

        candidate_path = (
            self.saved_models_root
            / cleaned_name
        ).resolve()

        if (
            candidate_path.parent
            != self.saved_models_root
        ):
            return (
                False,
                "Model directory must be a direct child of "
                "ml/saved_models.",
            )

        if not candidate_path.is_dir():
            return (
                False,
                "The candidate model directory does not exist.",
            )

        required_files = {
            "config.json",
        }

        missing = [
            filename
            for filename in required_files
            if not (
                candidate_path / filename
            ).is_file()
        ]

        tokenizer_exists = any(
            (
                candidate_path / filename
            ).is_file()
            for filename in (
                "tokenizer.json",
                "tokenizer_config.json",
                "vocab.txt",
            )
        )

        model_weights_exist = any(
            (
                candidate_path / filename
            ).is_file()
            for filename in (
                "model.safetensors",
                "pytorch_model.bin",
            )
        )

        if missing:
            return (
                False,
                "The model directory is missing config.json.",
            )

        if not tokenizer_exists:
            return (
                False,
                "The model directory does not contain tokenizer files.",
            )

        if not model_weights_exist:
            return (
                False,
                "The model directory does not contain model weights.",
            )

        return (
            True,
            "Candidate model directory validated.",
        )

    def count_candidate_rows(self):
        """
        Return the number of records currently available for
        privacy-reduced retraining preparation.
        """

        return len(
            get_candidate_retraining_rows()
        )

    def _redact_text(
        self,
        text: str,
    ) -> str:
        """
        Mask common direct identifiers in free-form text.
        """

        redacted = text.strip()

        redacted = self.EMAIL_PATTERN.sub(
            "[REDACTED_EMAIL]",
            redacted,
        )

        redacted = self.URL_PATTERN.sub(
            "[REDACTED_URL]",
            redacted,
        )

        redacted = self.PHONE_PATTERN.sub(
            "[REDACTED_PHONE]",
            redacted,
        )

        redacted = self.HANDLE_PATTERN.sub(
            "[REDACTED_HANDLE]",
            redacted,
        )

        return redacted
