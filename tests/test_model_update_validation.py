import tempfile
import unittest
from pathlib import Path

from app.services.model_update_service import (
    ModelUpdateService,
)


class ModelUpdateValidationTests(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.service = ModelUpdateService()
        self.service.saved_models_root = self.root.resolve()

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_blank_directory_name_is_rejected(self):
        valid, message = self.service.validate_model_directory(" ")
        self.assertFalse(valid)
        self.assertIn("required", message.lower())

    def test_path_traversal_is_rejected(self):
        valid, message = self.service.validate_model_directory(
            "../outside-model"
        )
        self.assertFalse(valid)
        self.assertIn("direct child", message.lower())

    def test_missing_directory_is_rejected(self):
        valid, message = self.service.validate_model_directory(
            "does-not-exist"
        )
        self.assertFalse(valid)
        self.assertIn("does not exist", message.lower())

    def test_missing_model_files_are_rejected(self):
        candidate = self.root / "candidate"
        candidate.mkdir()

        valid, message = self.service.validate_model_directory(
            "candidate"
        )

        self.assertFalse(valid)
        self.assertIn("config.json", message)

    def test_valid_local_model_directory_is_accepted(self):
        candidate = self.root / "candidate"
        candidate.mkdir()
        (candidate / "config.json").write_text(
            "{}",
            encoding="utf-8",
        )
        (candidate / "tokenizer.json").write_text(
            "{}",
            encoding="utf-8",
        )
        (candidate / "model.safetensors").write_bytes(
            b"test"
        )

        valid, message = self.service.validate_model_directory(
            "candidate"
        )

        self.assertTrue(valid)
        self.assertIn("validated", message.lower())

    def test_redaction_masks_common_direct_identifiers(self):
        text = (
            "Email me at name@example.com or call +94 77 123 4567. "
            "See https://example.com and message @sample_user."
        )

        redacted = self.service._redact_text(text)

        self.assertNotIn("name@example.com", redacted)
        self.assertNotIn("+94 77 123 4567", redacted)
        self.assertNotIn("https://example.com", redacted)
        self.assertNotIn("@sample_user", redacted)

        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertIn("[REDACTED_URL]", redacted)
        self.assertIn("[REDACTED_HANDLE]", redacted)


if __name__ == "__main__":
    unittest.main()
