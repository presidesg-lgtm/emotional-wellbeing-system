from app.repositories.database import get_database_connection


def get_admin_system_overview():
    """
    Return aggregate platform counts for the administrator
    analytics report.

    No private mood-entry text is selected.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_analyses,
            COUNT(DISTINCT user_id) AS users_with_mood_analyses
        FROM mood_entries
        """
    )
    mood = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_appointments,
            COUNT(DISTINCT user_id) AS users_with_appointments,
            SUM(status = 'pending') AS pending_appointments,
            SUM(status = 'confirmed') AS confirmed_appointments,
            SUM(status = 'completed') AS completed_appointments,
            SUM(status = 'rejected') AS rejected_appointments,
            SUM(status = 'cancelled') AS cancelled_appointments
        FROM appointments
        """
    )
    appointments = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_forum_posts,
            COUNT(DISTINCT user_id) AS users_with_forum_posts,
            SUM(is_hidden = FALSE) AS visible_forum_posts,
            SUM(is_hidden = TRUE) AS hidden_forum_posts
        FROM forum_posts
        """
    )
    forum_posts = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_forum_reports,
            SUM(status = 'pending') AS pending_forum_reports
        FROM forum_reports
        """
    )
    forum_reports = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_assignments
        FROM user_counsellor_assignments
        """
    )
    assignments = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "total_analyses": int(
            mood["total_analyses"] or 0
        ),
        "users_with_mood_analyses": int(
            mood["users_with_mood_analyses"] or 0
        ),
        "total_appointments": int(
            appointments["total_appointments"] or 0
        ),
        "users_with_appointments": int(
            appointments["users_with_appointments"] or 0
        ),
        "pending_appointments": int(
            appointments["pending_appointments"] or 0
        ),
        "confirmed_appointments": int(
            appointments["confirmed_appointments"] or 0
        ),
        "completed_appointments": int(
            appointments["completed_appointments"] or 0
        ),
        "rejected_appointments": int(
            appointments["rejected_appointments"] or 0
        ),
        "cancelled_appointments": int(
            appointments["cancelled_appointments"] or 0
        ),
        "total_forum_posts": int(
            forum_posts["total_forum_posts"] or 0
        ),
        "users_with_forum_posts": int(
            forum_posts["users_with_forum_posts"] or 0
        ),
        "visible_forum_posts": int(
            forum_posts["visible_forum_posts"] or 0
        ),
        "hidden_forum_posts": int(
            forum_posts["hidden_forum_posts"] or 0
        ),
        "total_forum_reports": int(
            forum_reports["total_forum_reports"] or 0
        ),
        "pending_forum_reports": int(
            forum_reports["pending_forum_reports"] or 0
        ),
        "total_assignments": int(
            assignments["total_assignments"] or 0
        ),
    }


def get_admin_engagement_summary():
    """
    Return privacy-aware user engagement counts.

    Engagement is based on whether a normal user has used at
    least one of the mood-analysis, appointment, or forum
    features. Private submitted text is never selected.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_normal_users,
            SUM(is_active = TRUE) AS active_normal_users
        FROM users
        WHERE role = 'user'
        """
    )
    users = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) AS engaged_users
        FROM (
            SELECT DISTINCT me.user_id
            FROM mood_entries me

            UNION

            SELECT DISTINCT a.user_id
            FROM appointments a

            UNION

            SELECT DISTINCT fp.user_id
            FROM forum_posts fp
        ) engaged
        JOIN users u
            ON u.id = engaged.user_id
        WHERE u.role = 'user'
        """
    )
    engaged = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            (
                SELECT COUNT(*)
                FROM mood_entries
                WHERE created_at >= NOW() - INTERVAL 7 DAY
            ) AS mood_analyses_last_7_days,

            (
                SELECT COUNT(*)
                FROM appointments
                WHERE created_at >= NOW() - INTERVAL 7 DAY
            ) AS appointments_last_7_days,

            (
                SELECT COUNT(*)
                FROM forum_posts
                WHERE created_at >= NOW() - INTERVAL 7 DAY
            ) AS forum_posts_last_7_days
        """
    )
    recent = cursor.fetchone()

    cursor.close()
    connection.close()

    total_normal_users = int(
        users["total_normal_users"] or 0
    )

    engaged_users = int(
        engaged["engaged_users"] or 0
    )

    engagement_rate = (
        round(
            (engaged_users / total_normal_users) * 100,
            1,
        )
        if total_normal_users
        else 0.0
    )

    return {
        "total_normal_users": total_normal_users,
        "active_normal_users": int(
            users["active_normal_users"] or 0
        ),
        "engaged_users": engaged_users,
        "engagement_rate": engagement_rate,
        "mood_analyses_last_7_days": int(
            recent["mood_analyses_last_7_days"] or 0
        ),
        "appointments_last_7_days": int(
            recent["appointments_last_7_days"] or 0
        ),
        "forum_posts_last_7_days": int(
            recent["forum_posts_last_7_days"] or 0
        ),
    }


def get_admin_emotion_distribution():
    """
    Return aggregate predicted-emotion counts and percentages.

    This query deliberately excludes submitted_text and user
    identity so administrators only receive population-level
    emotion-label statistics.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            predicted_emotion,
            COUNT(*) AS emotion_count
        FROM mood_entries
        GROUP BY predicted_emotion
        ORDER BY
            emotion_count DESC,
            predicted_emotion ASC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    total = sum(
        int(row["emotion_count"] or 0)
        for row in rows
    )

    distribution = []

    for row in rows:
        count = int(
            row["emotion_count"] or 0
        )

        percentage = (
            round((count / total) * 100, 1)
            if total
            else 0.0
        )

        distribution.append(
            {
                "emotion": row["predicted_emotion"],
                "count": count,
                "percentage": percentage,
            }
        )

    return distribution


def get_admin_appointment_status_distribution():
    """
    Return appointment counts grouped by status.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            status,
            COUNT(*) AS appointment_count
        FROM appointments
        GROUP BY status
        ORDER BY
            CASE status
                WHEN 'pending' THEN 1
                WHEN 'confirmed' THEN 2
                WHEN 'completed' THEN 3
                WHEN 'rejected' THEN 4
                WHEN 'cancelled' THEN 5
                ELSE 6
            END
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    total = sum(
        int(row["appointment_count"] or 0)
        for row in rows
    )

    result = []

    for row in rows:
        count = int(
            row["appointment_count"] or 0
        )

        result.append(
            {
                "status": row["status"],
                "count": count,
                "percentage": (
                    round((count / total) * 100, 1)
                    if total
                    else 0.0
                ),
            }
        )

    return result


def get_admin_counsellor_workload():
    """
    Return appointment workload statistics for each
    counsellor account.

    Workload data contains appointment counts only and does
    not expose private user mood text.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            cp.id AS counsellor_profile_id,
            u.full_name AS counsellor_name,
            cp.specialization,
            u.is_active,
            cp.is_available,

            COUNT(a.id) AS total_appointments,

            SUM(
                CASE
                    WHEN a.status = 'pending'
                    THEN 1
                    ELSE 0
                END
            ) AS pending_appointments,

            SUM(
                CASE
                    WHEN a.status = 'confirmed'
                    THEN 1
                    ELSE 0
                END
            ) AS confirmed_appointments,

            SUM(
                CASE
                    WHEN a.status = 'completed'
                    THEN 1
                    ELSE 0
                END
            ) AS completed_appointments,

            COUNT(DISTINCT uca.user_id) AS assigned_users

        FROM counsellor_profiles cp

        JOIN users u
            ON u.id = cp.user_id

        LEFT JOIN appointments a
            ON a.counsellor_profile_id = cp.id

        LEFT JOIN user_counsellor_assignments uca
            ON uca.counsellor_profile_id = cp.id

        WHERE u.role = 'counsellor'

        GROUP BY
            cp.id,
            u.full_name,
            cp.specialization,
            u.is_active,
            cp.is_available

        ORDER BY
            total_appointments DESC,
            u.full_name ASC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    for row in rows:
        row["total_appointments"] = int(
            row["total_appointments"] or 0
        )
        row["pending_appointments"] = int(
            row["pending_appointments"] or 0
        )
        row["confirmed_appointments"] = int(
            row["confirmed_appointments"] or 0
        )
        row["completed_appointments"] = int(
            row["completed_appointments"] or 0
        )
        row["assigned_users"] = int(
            row["assigned_users"] or 0
        )

    return rows


def get_admin_recent_activity():
    """
    Return aggregate platform activity totals for each day
    represented during the last seven days.

    No private mood text or individual user identity is returned.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            activity_date,
            SUM(mood_analyses) AS mood_analyses,
            SUM(appointments) AS appointments,
            SUM(forum_posts) AS forum_posts
        FROM (
            SELECT
                DATE(created_at) AS activity_date,
                COUNT(*) AS mood_analyses,
                0 AS appointments,
                0 AS forum_posts
            FROM mood_entries
            WHERE created_at >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(created_at)

            UNION ALL

            SELECT
                DATE(created_at) AS activity_date,
                0 AS mood_analyses,
                COUNT(*) AS appointments,
                0 AS forum_posts
            FROM appointments
            WHERE created_at >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(created_at)

            UNION ALL

            SELECT
                DATE(created_at) AS activity_date,
                0 AS mood_analyses,
                0 AS appointments,
                COUNT(*) AS forum_posts
            FROM forum_posts
            WHERE created_at >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(created_at)
        ) activity
        GROUP BY activity_date
        ORDER BY activity_date DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    for row in rows:
        row["mood_analyses"] = int(
            row["mood_analyses"] or 0
        )
        row["appointments"] = int(
            row["appointments"] or 0
        )
        row["forum_posts"] = int(
            row["forum_posts"] or 0
        )

    return rows
