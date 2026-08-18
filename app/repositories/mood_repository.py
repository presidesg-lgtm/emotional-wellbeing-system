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