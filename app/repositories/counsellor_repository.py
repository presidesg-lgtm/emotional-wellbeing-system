from app.repositories.database import get_database_connection


def _format_start_time(start_time):
    """
    Convert MySQL TIME values returned as timedelta objects
    into HH:MM text for display.
    """

    total_seconds = int(
        start_time.total_seconds()
    )

    hours = total_seconds // 3600

    minutes = (
        total_seconds % 3600
    ) // 60

    return f"{hours:02d}:{minutes:02d}"


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


def get_counsellor_profile_by_user_id(
    counsellor_user_id: int,
):
    """
    Return the counsellor profile belonging to
    the supplied counsellor user account.
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
            cp.user_id = %s
            AND u.role = 'counsellor'
            AND u.is_active = TRUE
        LIMIT 1
        """,
        (counsellor_user_id,),
    )

    counsellor = cursor.fetchone()

    cursor.close()
    connection.close()

    return counsellor


def create_availability_slot(
    counsellor_profile_id: int,
    slot_date: str,
    start_time: str,
):
    """
    Create one availability slot for a counsellor.

    INSERT IGNORE prevents duplicate date/time slots
    for the same counsellor.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT IGNORE INTO counsellor_availability_slots (
            counsellor_profile_id,
            slot_date,
            start_time
        )
        VALUES (%s, %s, %s)
        """,
        (
            counsellor_profile_id,
            slot_date,
            start_time,
        ),
    )

    connection.commit()

    created = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return created


def get_availability_slots_for_counsellor(
    counsellor_profile_id: int,
):
    """
    Return current and future availability slots
    belonging to one counsellor.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            counsellor_profile_id,
            slot_date,
            start_time,
            is_booked,
            created_at
        FROM counsellor_availability_slots
        WHERE
            counsellor_profile_id = %s
            AND slot_date >= CURDATE()
        ORDER BY
            slot_date ASC,
            start_time ASC
        """,
        (counsellor_profile_id,),
    )

    slots = cursor.fetchall()

    for slot in slots:
        slot["formatted_start_time"] = (
            _format_start_time(
                slot["start_time"]
            )
        )

    cursor.close()
    connection.close()

    return slots


def get_available_slots_for_profile(
    counsellor_profile_id: int,
):
    """
    Return bookable current/future slots for
    an active and available counsellor.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            cas.id,
            cas.counsellor_profile_id,
            cas.slot_date,
            cas.start_time,
            cas.is_booked
        FROM counsellor_availability_slots cas
        JOIN counsellor_profiles cp
            ON cp.id = cas.counsellor_profile_id
        JOIN users u
            ON u.id = cp.user_id
        WHERE
            cas.counsellor_profile_id = %s
            AND cas.is_booked = FALSE
            AND cas.slot_date >= CURDATE()
            AND cp.is_available = TRUE
            AND u.is_active = TRUE
            AND u.role = 'counsellor'
        ORDER BY
            cas.slot_date ASC,
            cas.start_time ASC
        """,
        (counsellor_profile_id,),
    )

    slots = cursor.fetchall()

    for slot in slots:
        slot["formatted_start_time"] = (
            _format_start_time(
                slot["start_time"]
            )
        )

    cursor.close()
    connection.close()

    return slots


def delete_unbooked_availability_slot(
    slot_id: int,
    counsellor_profile_id: int,
):
    """
    Delete an availability slot only when it belongs
    to the counsellor and has not been booked.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM counsellor_availability_slots
        WHERE
            id = %s
            AND counsellor_profile_id = %s
            AND is_booked = FALSE
        """,
        (
            slot_id,
            counsellor_profile_id,
        ),
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return deleted