from pathlib import Path

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from app.repositories.model_update_repository import (
    get_active_model_directory,
)


CLASS_NAMES = [
    "Sadness",
    "Joy",
    "Love",
    "Anger",
    "Fear",
    "Surprise",
]


class EmotionAnalysisService:
    """
    Load the active validated DistilBERT model and produce
    emotion predictions for user-submitted text.

    If an administrator deploys a different evaluated local model,
    the service reloads it automatically before the next analysis.
    """

    def __init__(self) -> None:
        self.project_root = (
            Path(__file__).resolve().parents[2]
        )

        self.saved_models_root = (
            self.project_root
            / "ml"
            / "saved_models"
        ).resolve()

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model_directory_name = None
        self.model_directory = None
        self.tokenizer = None
        self.model = None

        self._ensure_active_model_loaded()

    def _ensure_active_model_loaded(self):
        """
        Load or reload the model when the active model registry
        entry changes.
        """

        active_directory_name = (
            get_active_model_directory()
        )

        if (
            self.model is not None
            and self.model_directory_name
            == active_directory_name
        ):
            return

        candidate_directory = (
            self.saved_models_root
            / active_directory_name
        ).resolve()

        if (
            candidate_directory.parent
            != self.saved_models_root
            or not candidate_directory.is_dir()
        ):
            candidate_directory = (
                self.saved_models_root
                / "selected-distilbert-emotion"
            ).resolve()

            active_directory_name = (
                "selected-distilbert-emotion"
            )

        tokenizer = AutoTokenizer.from_pretrained(
            candidate_directory
        )

        model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                candidate_directory
            )
        )

        model.to(self.device)
        model.eval()

        self.tokenizer = tokenizer
        self.model = model
        self.model_directory = (
            candidate_directory
        )
        self.model_directory_name = (
            active_directory_name
        )

    def analyse_text(self, text: str) -> dict:
        """
        Analyse text and return the predicted emotion and confidence.
        """

        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError(
                "Text must not be empty."
            )

        self._ensure_active_model_loaded()

        encoded_input = self.tokenizer(
            cleaned_text,
            truncation=True,
            padding=True,
            max_length=64,
            return_tensors="pt",
        )

        encoded_input = {
            key: value.to(self.device)
            for key, value
            in encoded_input.items()
            if key in {
                "input_ids",
                "attention_mask",
            }
        }

        with torch.no_grad():
            output = self.model(
                **encoded_input
            )

            probabilities = torch.softmax(
                output.logits,
                dim=-1,
            )

            confidence, predicted_class = (
                torch.max(
                    probabilities,
                    dim=-1,
                )
            )

        predicted_index = (
            predicted_class.item()
        )

        return {
            "emotion": (
                CLASS_NAMES[
                    predicted_index
                ]
            ),
            "confidence": round(
                confidence.item(),
                4,
            ),
        }
