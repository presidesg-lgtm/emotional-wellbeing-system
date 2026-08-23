from app.repositories.database import get_database_connection


def create_mood_entry(
    user_id: int,
    submitted_text: str,
    predicted_emotion: str,
    confidence: float,
):
    """
    Store a completed emotion analysis for a user.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO mood_entries (
            user_id,
            submitted_text,
            predicted_emotion,
            confidence
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            user_id,
            submitted_text,
            predicted_emotion,
            confidence,
        ),
    )

    connection.commit()

    mood_entry_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return mood_entry_id

def get_mood_entries_by_user(
    user_id: int,
    limit: int = 50,
):
    """
    Return the most recent mood entries belonging
    to one authenticated user.
    """

    connection = get_database_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            submitted_text,
            predicted_emotion,
            confidence,
            created_at
        FROM mood_entries
        WHERE user_id = %s
        ORDER BY created_at DESC, id DESC
        LIMIT %s
        """,
        (
            user_id,
            limit,
        ),
    )

    mood_entries = cursor.fetchall()

    cursor.close()
    connection.close()

    return mood_entries

def get_mood_summary_by_user(
    user_id: int,
):
    """
    Return summary statistics for one user's mood entries.
    """

    connection = get_database_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_analyses,
            AVG(confidence) AS average_confidence
        FROM mood_entries
        WHERE user_id = %s
        """,
        (user_id,),
    )

    summary = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            predicted_emotion,
            COUNT(*) AS emotion_count
        FROM mood_entries
        WHERE user_id = %s
        GROUP BY predicted_emotion
        ORDER BY emotion_count DESC, predicted_emotion ASC
        LIMIT 1
        """,
        (user_id,),
    )

    most_common = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "total_analyses": summary["total_analyses"] or 0,
        "average_confidence": (
            float(summary["average_confidence"])
            if summary["average_confidence"] is not None
            else 0.0
        ),
        "most_common_emotion": (
            most_common["predicted_emotion"]
            if most_common is not None
            else "No data"
        ),
    }

def get_emotion_distribution_by_user(
    user_id: int,
):
    """
    Return the count of each predicted emotion
    for one authenticated user.
    """

    connection = get_database_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            predicted_emotion,
            COUNT(*) AS emotion_count
        FROM mood_entries
        WHERE user_id = %s
        GROUP BY predicted_emotion
        ORDER BY predicted_emotion
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    emotion_counts = {
        "Sadness": 0,
        "Joy": 0,
        "Love": 0,
        "Anger": 0,
        "Fear": 0,
        "Surprise": 0,
    }

    for row in rows:
        emotion_counts[
            row["predicted_emotion"]
        ] = row["emotion_count"]

    return emotion_counts

def get_weekly_mood_summary_by_user(
    user_id: int,
):
    """
    Return a privacy-aware summary of the authenticated user's
    mood analyses recorded during the last seven days.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_analyses,
            AVG(confidence) AS average_confidence,
            COUNT(DISTINCT predicted_emotion) AS distinct_emotions
        FROM mood_entries
        WHERE
            user_id = %s
            AND created_at >= NOW() - INTERVAL 7 DAY
        """,
        (user_id,),
    )

    summary = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            predicted_emotion,
            COUNT(*) AS emotion_count
        FROM mood_entries
        WHERE
            user_id = %s
            AND created_at >= NOW() - INTERVAL 7 DAY
        GROUP BY predicted_emotion
        ORDER BY
            emotion_count DESC,
            predicted_emotion ASC
        LIMIT 1
        """,
        (user_id,),
    )

    most_common = cursor.fetchone()

    cursor.close()
    connection.close()

    total_analyses = int(
        summary["total_analyses"] or 0
    )

    average_confidence = (
        float(summary["average_confidence"])
        if summary["average_confidence"] is not None
        else 0.0
    )

    distinct_emotions = int(
        summary["distinct_emotions"] or 0
    )

    most_common_emotion = (
        most_common["predicted_emotion"]
        if most_common is not None
        else "No data"
    )

    if total_analyses == 0:
        summary_text = (
            "No emotion analyses were recorded during the "
            "last 7 days. Complete an analysis to begin "
            "building your weekly emotional pattern summary."
        )

    elif total_analyses == 1:
        summary_text = (
            "During the last 7 days, you completed 1 emotion "
            f"analysis. {most_common_emotion} was the identified "
            "emotional expression. This summary is intended for "
            "reflection and is not a medical diagnosis."
        )

    else:
        summary_text = (
            f"During the last 7 days, {most_common_emotion} was "
            f"the most frequently identified emotion across "
            f"{total_analyses} analyses. Your recorded emotional "
            f"language covered {distinct_emotions} emotion "
            "categories. This summary is intended for reflection "
            "and is not a medical diagnosis."
        )

    return {
        "total_analyses": total_analyses,
        "average_confidence": average_confidence,
        "distinct_emotions": distinct_emotions,
        "most_common_emotion": most_common_emotion,
        "summary_text": summary_text,
    }


def get_seven_day_mood_trend_by_user(
    user_id: int,
):
    """
    Return one row for each of the last seven calendar days.

    Each row contains the number of analyses recorded on that
    day and the day's most frequent predicted emotion.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        WITH RECURSIVE last_seven_days AS (
            SELECT CURDATE() - INTERVAL 6 DAY AS trend_date

            UNION ALL

            SELECT trend_date + INTERVAL 1 DAY
            FROM last_seven_days
            WHERE trend_date < CURDATE()
        ),

        daily_counts AS (
            SELECT
                DATE(created_at) AS analysis_date,
                COUNT(*) AS analysis_count
            FROM mood_entries
            WHERE
                user_id = %s
                AND created_at >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(created_at)
        ),

        daily_emotions AS (
            SELECT
                DATE(created_at) AS analysis_date,
                predicted_emotion,
                COUNT(*) AS emotion_count,
                ROW_NUMBER() OVER (
                    PARTITION BY DATE(created_at)
                    ORDER BY
                        COUNT(*) DESC,
                        predicted_emotion ASC
                ) AS emotion_rank
            FROM mood_entries
            WHERE
                user_id = %s
                AND created_at >= CURDATE() - INTERVAL 6 DAY
            GROUP BY
                DATE(created_at),
                predicted_emotion
        )

        SELECT
            d.trend_date,
            COALESCE(dc.analysis_count, 0) AS analysis_count,
            de.predicted_emotion AS dominant_emotion
        FROM last_seven_days d

        LEFT JOIN daily_counts dc
            ON dc.analysis_date = d.trend_date

        LEFT JOIN daily_emotions de
            ON de.analysis_date = d.trend_date
            AND de.emotion_rank = 1

        ORDER BY d.trend_date ASC
        """,
        (
            user_id,
            user_id,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    for row in rows:
        row["analysis_count"] = int(
            row["analysis_count"] or 0
        )

        if row["dominant_emotion"] is None:
            row["dominant_emotion"] = "No analysis"

    return rows
