import io
import unittest

from werkzeug.datastructures import FileStorage

from app.services.upload_validation_service import (
    MAX_PAYMENT_PROOF_BYTES,
    validate_payment_proof,
)


def make_upload(filename, content):
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
    )


class UploadValidationTests(unittest.TestCase):

    def test_valid_pdf_is_accepted(self):
        result = validate_payment_proof(
            make_upload("proof.pdf", b"%PDF-1.7\nexample")
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.detected_extension, "pdf")

    def test_valid_png_is_accepted(self):
        result = validate_payment_proof(
            make_upload(
                "proof.png",
                b"\x89PNG\r\n\x1a\nexample",
            )
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.detected_extension, "png")

    def test_valid_jpeg_is_accepted(self):
        result = validate_payment_proof(
            make_upload(
                "proof.jpeg",
                b"\xff\xd8\xff\xe0example",
            )
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.detected_extension, "jpg")

    def test_fake_image_extension_is_rejected(self):
        result = validate_payment_proof(
            make_upload(
                "fake.jpg",
                b"MZ executable content",
            )
        )
        self.assertFalse(result.is_valid)
        self.assertIn("content", result.message.lower())

    def test_extension_content_mismatch_is_rejected(self):
        result = validate_payment_proof(
            make_upload(
                "proof.pdf",
                b"\x89PNG\r\n\x1a\nexample",
            )
        )
        self.assertFalse(result.is_valid)
        self.assertIn("extension", result.message.lower())

    def test_empty_file_is_rejected(self):
        result = validate_payment_proof(
            make_upload("proof.pdf", b"")
        )
        self.assertFalse(result.is_valid)
        self.assertIn("empty", result.message.lower())

    def test_unsupported_extension_is_rejected(self):
        result = validate_payment_proof(
            make_upload("proof.exe", b"%PDF-1.7\nexample")
        )
        self.assertFalse(result.is_valid)

    def test_oversized_file_is_rejected(self):
        result = validate_payment_proof(
            make_upload(
                "proof.jpg",
                b"\xff\xd8\xff" + (
                    b"A" * (MAX_PAYMENT_PROOF_BYTES + 1)
                ),
            )
        )
        self.assertFalse(result.is_valid)
        self.assertIn("5 mb", result.message.lower())


if __name__ == "__main__":
    unittest.main()
