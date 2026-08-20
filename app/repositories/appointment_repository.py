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


def create_appointment(
    user_id: int,
    counsellor_profile_id: int,
    appointment_date: str,
    start_time: str,
):
    """
    Create a new pending appointment request.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO appointments (
            user_id,
            counsellor_profile_id,
            appointment_date,
            start_time,
            status
        )
        VALUES (%s, %s, %s, %s, 'pending')
        """,
        (
            user_id,
            counsellor_profile_id,
            appointment_date,
            start_time,
        ),
    )

    connection.commit()

    appointment_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return appointment_id


def get_appointments_by_user(
    user_id: int,
):
    """
    Return appointment requests belonging to one user.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            a.id,
            a.appointment_date,
            a.start_time,
            a.status,
            a.created_at,
            cp.id AS counsellor_profile_id,
            u.full_name AS counsellor_name,
            cp.specialization
        FROM appointments a
        JOIN counsellor_profiles cp
            ON cp.id = a.counsellor_profile_id
        JOIN users u
            ON u.id = cp.user_id
        WHERE a.user_id = %s
        ORDER BY
            a.appointment_date DESC,
            a.start_time DESC
        """,
        (user_id,),
    )

    appointments = cursor.fetchall()

    for appointment in appointments:
        appointment["formatted_start_time"] = (
            _format_start_time(
                appointment["start_time"]
            )
        )

    cursor.close()
    connection.close()

    return appointments


def get_appointments_for_counsellor(
    counsellor_user_id: int,
):
    """
    Return appointments assigned to the logged-in counsellor.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            a.id,
            a.user_id,
            u.full_name AS user_name,
            u.email AS user_email,
            a.appointment_date,
            a.start_time,
            a.status,
            a.created_at,
            cp.id AS counsellor_profile_id,
            cp.specialization
        FROM appointments a
        JOIN counsellor_profiles cp
            ON cp.id = a.counsellor_profile_id
        JOIN users u
            ON u.id = a.user_id
        WHERE cp.user_id = %s
        ORDER BY
            CASE a.status
                WHEN 'pending' THEN 1
                WHEN 'confirmed' THEN 2
                WHEN 'completed' THEN 3
                WHEN 'cancelled' THEN 4
                WHEN 'rejected' THEN 5
                ELSE 6
            END,
            a.appointment_date ASC,
            a.start_time ASC
        """,
        (counsellor_user_id,),
    )

    appointments = cursor.fetchall()

    for appointment in appointments:
        appointment["formatted_start_time"] = (
            _format_start_time(
                appointment["start_time"]
            )
        )

    cursor.close()
    connection.close()

    return appointments


def update_appointment_status(
    appointment_id: int,
    counsellor_user_id: int,
    status: str,
):
    """
    Update an appointment status only when the appointment
    belongs to the logged-in counsellor.
    """

    allowed_statuses = {
        "confirmed",
        "rejected",
        "completed",
        "cancelled",
    }

    if status not in allowed_statuses:
        return False

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE appointments a
        JOIN counsellor_profiles cp
            ON cp.id = a.counsellor_profile_id
        SET a.status = %s
        WHERE
            a.id = %s
            AND cp.user_id = %s
        """,
        (
            status,
            appointment_id,
            counsellor_user_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return updated