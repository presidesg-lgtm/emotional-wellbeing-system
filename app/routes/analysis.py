from flask import Blueprint, jsonify, request, session

from app.repositories.mood_repository import create_mood_entry
from app.services.emotion_analysis_service import EmotionAnalysisService


analysis_blueprint = Blueprint(
    "analysis",
    __name__,
)

_emotion_service = None


def get_emotion_service():
    """
    Create the emotion-analysis service only when it is first needed.

    This prevents the transformer model from being loaded during
    unrelated application tasks such as database scripts.
    """

    global _emotion_service

    if _emotion_service is None:
        _emotion_service = EmotionAnalysisService()

    return _emotion_service


@analysis_blueprint.post("/api/analyse")
def analyse_text():
    """
    Analyse user-submitted text, return the prediction,
    and store the result for the authenticated user.
    """

    if "user_id" not in session:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "You must be logged in to analyse text.",
                }
            ),
            401,
        )

    request_data = request.get_json(silent=True) or {}

    text = request_data.get("text", "")

    try:
        emotion_service = get_emotion_service()

        result = emotion_service.analyse_text(text)

        mood_entry_id = create_mood_entry(
            user_id=session["user_id"],
            submitted_text=text.strip(),
            predicted_emotion=result["emotion"],
            confidence=result["confidence"],
        )

        return jsonify(
            {
                "success": True,
                "mood_entry_id": mood_entry_id,
                "emotion": result["emotion"],
                "confidence": result["confidence"],
                "disclaimer": (
                    "This result reflects patterns of emotional language "
                    "and is not a medical or psychological diagnosis."
                ),
            }
        )

    except ValueError as error:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(error),
                }
            ),
            400,
        )