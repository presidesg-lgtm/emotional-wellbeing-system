from dataclasses import dataclass
from pathlib import Path


MAX_PAYMENT_PROOF_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class PaymentProofValidationResult:
    is_valid: bool
    message: str
    detected_extension: str | None = None


_ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
}


def _detect_file_type(header: bytes) -> str | None:
    """
    Identify the supported file type from its binary signature.

    Browser-provided MIME types and filenames are not trusted because
    they can be changed by the client.
    """

    if header.startswith(b"%PDF-"):
        return "pdf"

    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if header.startswith(b"\xff\xd8\xff"):
        return "jpg"

    return None


def validate_payment_proof(uploaded_file) -> PaymentProofValidationResult:
    """
    Validate a payment-proof upload by filename, size, and file signature.

    The file stream is restored to position zero before returning so the
    caller can save a valid upload normally.
    """

    filename = (uploaded_file.filename or "").strip()

    if not filename:
        return PaymentProofValidationResult(
            False,
            "Please select a payment proof file.",
        )

    suffix = Path(filename).suffix.lower().lstrip(".")

    if suffix not in _ALLOWED_EXTENSIONS:
        return PaymentProofValidationResult(
            False,
            "Only PDF, PNG, JPG, and JPEG files are allowed.",
        )

    stream = uploaded_file.stream

    try:
        stream.seek(0, 2)
        size = stream.tell()
        stream.seek(0)
    except (AttributeError, OSError):
        return PaymentProofValidationResult(
            False,
            "The uploaded file could not be read.",
        )

    if size <= 0:
        return PaymentProofValidationResult(
            False,
            "The selected payment proof file is empty.",
        )

    if size > MAX_PAYMENT_PROOF_BYTES:
        return PaymentProofValidationResult(
            False,
            "Payment proof files must not exceed 5 MB.",
        )

    header = stream.read(16)
    stream.seek(0)

    detected_extension = _detect_file_type(header)

    if detected_extension is None:
        return PaymentProofValidationResult(
            False,
            (
                "The uploaded file content is not a valid PDF, PNG, "
                "JPG, or JPEG file."
            ),
        )

    filename_type = "jpg" if suffix == "jpeg" else suffix

    if filename_type != detected_extension:
        return PaymentProofValidationResult(
            False,
            (
                "The file extension does not match the uploaded "
                "file content."
            ),
        )

    return PaymentProofValidationResult(
        True,
        "Payment proof file is valid.",
        detected_extension=detected_extension,
    )
