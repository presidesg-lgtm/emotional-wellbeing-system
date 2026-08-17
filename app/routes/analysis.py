from flask import Blueprint, jsonify, request

from app.services.emotion_analysis_service import EmotionAnalysisService


analysis_blueprint = Blueprint(
    "analysis",
    __name__,
)

emotion_service = EmotionAnalysisService()


@analysis_blueprint.post("/api/analyse")
def analyse_text():
    """
    Analyse user-submitted text and return an emotion prediction.
    """

    request_data = request.get_json(silent=True) or {}

    text = request_data.get("text", "")

    try:
        result = emotion_service.analyse_text(text)

        return jsonify(
            {
                "success": True,
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