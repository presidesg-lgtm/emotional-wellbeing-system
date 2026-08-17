from pathlib import Path

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
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
    Service responsible for loading the selected DistilBERT model
    and producing emotion predictions for user-submitted text.
    """

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]

        self.model_directory = (
            project_root
            / "ml"
            / "saved_models"
            / "selected-distilbert-emotion"
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_directory
        )

        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_directory
        )

        self.model.to(self.device)
        self.model.eval()

    def analyse_text(self, text: str) -> dict:
        """
        Analyse text and return the predicted emotion and confidence.
        """

        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError("Text must not be empty.")

        encoded_input = self.tokenizer(
            cleaned_text,
            truncation=True,
            padding=True,
            max_length=64,
            return_tensors="pt",
        )

        encoded_input = {
            key: value.to(self.device)
            for key, value in encoded_input.items()
            if key in {"input_ids", "attention_mask"}
        }

        with torch.no_grad():
            output = self.model(**encoded_input)

            probabilities = torch.softmax(
                output.logits,
                dim=-1,
            )

            confidence, predicted_class = torch.max(
                probabilities,
                dim=-1,
            )

        predicted_index = predicted_class.item()

        return {
            "emotion": CLASS_NAMES[predicted_index],
            "confidence": round(
                confidence.item(),
                4,
            ),
        }