class CounsellorRecommendationService:
    """
    Rank currently available counsellors using a transparent,
    non-diagnostic matching approach.

    Recommendations use the user's recent emotion pattern together
    with counsellor specialization text. They are intended to help
    the user browse support options, not to make a clinical referral.
    """

    EMOTION_SUPPORT_KEYWORDS = {
        "Fear": (
            "stress",
            "anxiety",
            "worry",
            "emotional wellbeing",
            "emotional well-being",
            "wellbeing",
            "well-being",
        ),
        "Sadness": (
            "low mood",
            "grief",
            "bereavement",
            "emotional wellbeing",
            "emotional well-being",
            "wellbeing",
            "well-being",
            "support",
        ),
        "Anger": (
            "anger",
            "stress",
            "conflict",
            "emotional regulation",
            "emotional wellbeing",
            "wellbeing",
        ),
        "Love": (
            "relationship",
            "relationships",
            "family",
            "interpersonal",
            "wellbeing",
            "well-being",
        ),
        "Joy": (
            "wellbeing",
            "well-being",
            "personal development",
            "self development",
            "general counselling",
        ),
        "Surprise": (
            "adjustment",
            "change",
            "stress",
            "emotional wellbeing",
            "wellbeing",
        ),
    }

    EMOTION_SUPPORT_LABELS = {
        "Fear": "stress, worry, or emotional wellbeing support",
        "Sadness": "low-mood or emotional wellbeing support",
        "Anger": "stress or emotional-regulation support",
        "Love": "relationship or interpersonal wellbeing support",
        "Joy": "general emotional wellbeing support",
        "Surprise": "adjustment, change, or emotional wellbeing support",
    }

    def recommend(
        self,
        counsellors: list,
        weekly_summary: dict,
    ) -> dict:
        """
        Return ranked counsellors and an explanation of the basis
        used for the recommendation.
        """

        if not counsellors:
            return {
                "basis_emotion": None,
                "basis_text": (
                    "No counsellors are currently available for "
                    "recommendation."
                ),
                "recommendations": [],
            }

        total_analyses = int(
            weekly_summary.get(
                "total_analyses",
                0,
            )
            or 0
        )

        emotion = weekly_summary.get(
            "most_common_emotion",
            "No data",
        )

        if (
            total_analyses <= 0
            or emotion == "No data"
        ):
            ranked = self._rank_general(
                counsellors
            )

            return {
                "basis_emotion": None,
                "basis_text": (
                    "Because there are no saved analyses from the "
                    "last 7 days, counsellors are shown using "
                    "availability and experience rather than an "
                    "emotion-based match."
                ),
                "recommendations": ranked,
            }

        keywords = self.EMOTION_SUPPORT_KEYWORDS.get(
            emotion,
            (
                "emotional wellbeing",
                "wellbeing",
                "well-being",
            ),
        )

        support_label = (
            self.EMOTION_SUPPORT_LABELS.get(
                emotion,
                "general emotional wellbeing support",
            )
        )

        ranked = []

        for counsellor in counsellors:
            specialization = (
                counsellor.get(
                    "specialization",
                    "",
                )
                or ""
            ).lower()

            matched_keywords = [
                keyword
                for keyword in keywords
                if keyword in specialization
            ]

            specialization_score = len(
                matched_keywords
            )

            years_experience = int(
                counsellor.get(
                    "years_experience",
                    0,
                )
                or 0
            )

            item = dict(counsellor)

            item[
                "recommendation_score"
            ] = specialization_score

            item[
                "recommendation_reason"
            ] = self._build_reason(
                counsellor=counsellor,
                emotion=emotion,
                support_label=support_label,
                matched_keywords=matched_keywords,
            )

            ranked.append(item)

        ranked.sort(
            key=lambda item: (
                -item["recommendation_score"],
                -int(
                    item.get(
                        "years_experience",
                        0,
                    )
                    or 0
                ),
                item.get(
                    "full_name",
                    "",
                ).lower(),
            )
        )

        return {
            "basis_emotion": emotion,
            "basis_text": (
                f"Your most frequently identified emotion during "
                f"the last 7 days was {emotion}. Available "
                f"counsellors are therefore ranked using "
                f"specializations related to {support_label}. "
                f"This is an assistive match, not a clinical "
                f"referral or diagnosis."
            ),
            "recommendations": ranked,
        }

    def _rank_general(
        self,
        counsellors: list,
    ) -> list:
        """
        Rank available counsellors by experience when there is
        no recent emotion pattern to use.
        """

        ranked = []

        for counsellor in counsellors:
            item = dict(counsellor)

            item[
                "recommendation_score"
            ] = 0

            item[
                "recommendation_reason"
            ] = (
                "Currently available for general counselling "
                "support. No recent emotion pattern was used "
                "for this recommendation."
            )

            ranked.append(item)

        ranked.sort(
            key=lambda item: (
                -int(
                    item.get(
                        "years_experience",
                        0,
                    )
                    or 0
                ),
                item.get(
                    "full_name",
                    "",
                ).lower(),
            )
        )

        return ranked

    @staticmethod
    def _build_reason(
        counsellor: dict,
        emotion: str,
        support_label: str,
        matched_keywords: list,
    ) -> str:
        """
        Build a readable explanation for one recommendation.
        """

        specialization = counsellor.get(
            "specialization",
            "general counselling",
        )

        if matched_keywords:
            return (
                f"Recommended because the counsellor's "
                f"specialization ({specialization}) overlaps "
                f"with {support_label}, based on your recent "
                f"{emotion} emotion pattern."
            )

        return (
            f"This counsellor is currently available. Their "
            f"specialization is {specialization}; although it "
            f"does not directly match the recent {emotion} "
            f"pattern keywords, they remain available as a "
            f"support option."
        )
