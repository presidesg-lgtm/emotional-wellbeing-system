from app.repositories.database import get_database_connection


def get_available_counsellors():
    """
    Return all active counsellors who are currently
    marked as available for appointments.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            cp.id AS profile_id,
            cp.user_id,
            u.full_name,
            u.email,
            cp.specialization,
            cp.qualifications,
            cp.bio,
            cp.years_experience,
            cp.is_available
        FROM counsellor_profiles cp
        JOIN users u
            ON u.id = cp.user_id
        WHERE
            u.role = 'counsellor'
            AND u.is_active = TRUE
            AND cp.is_available = TRUE
        ORDER BY
            u.full_name ASC
        """
    )

    counsellors = cursor.fetchall()

    cursor.close()
    connection.close()

    return counsellors


def get_counsellor_profile_by_id(
    profile_id: int,
):
    """
    Return one active counsellor profile by profile ID.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            cp.id AS profile_id,
            cp.user_id,
            u.full_name,
            u.email,
            cp.specialization,
            cp.qualifications,
            cp.bio,
            cp.years_experience,
            cp.is_available
        FROM counsellor_profiles cp
        JOIN users u
            ON u.id = cp.user_id
        WHERE
            cp.id = %s
            AND u.role = 'counsellor'
            AND u.is_active = TRUE
        LIMIT 1
        """,
        (profile_id,),
    )

    counsellor = cursor.fetchone()

    cursor.close()
    connection.close()

    return counsellor