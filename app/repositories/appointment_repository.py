from datetime import (
    datetime,
    time,
    timedelta,
)

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


def _build_appointment_datetime(
    appointment_date,
    start_time,
):
    """
    Combine a MySQL DATE value and TIME/timedelta value
    into a Python datetime.
    """

    total_seconds = int(
        start_time.total_seconds()
    )

    hours = total_seconds // 3600

    minutes = (
        total_seconds % 3600
    ) // 60

    seconds = total_seconds % 60

    appointment_time = time(
        hour=hours,
        minute=minutes,
        second=seconds,
    )

    return datetime.combine(
        appointment_date,
        appointment_time,
    )


def create_appointment(
    user_id: int,
    counsellor_profile_id: int,
    appointment_date: str,
    start_time: str,
):
    """
    Create a legacy/manual pending appointment request.

    Retained for compatibility with appointments created
    before the availability-slot workflow was introduced.
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


def create_appointment_from_slot(
    user_id: int,
    availability_slot_id: int,
):
    """
    Atomically reserve one available counsellor slot
    and create a pending appointment.

    The slot is locked during the transaction to prevent
    two users from booking the same appointment time.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

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
                cas.id = %s
                AND cas.is_booked = FALSE
                AND cas.slot_date >= CURDATE()
                AND cp.is_available = TRUE
                AND u.is_active = TRUE
                AND u.role = 'counsellor'
            LIMIT 1
            FOR UPDATE
            """,
            (availability_slot_id,),
        )

        slot = cursor.fetchone()

        if slot is None:
            connection.rollback()
            return None

        cursor.execute(
            """
            INSERT INTO appointments (
                user_id,
                counsellor_profile_id,
                availability_slot_id,
                appointment_date,
                start_time,
                status
            )
            VALUES (%s, %s, %s, %s, %s, 'pending')
            """,
            (
                user_id,
                slot["counsellor_profile_id"],
                slot["id"],
                slot["slot_date"],
                slot["start_time"],
            ),
        )

        appointment_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE counsellor_availability_slots
            SET is_booked = TRUE
            WHERE
                id = %s
                AND is_booked = FALSE
            """,
            (slot["id"],),
        )

        if cursor.rowcount != 1:
            connection.rollback()
            return None

        connection.commit()

        return appointment_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


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
            a.availability_slot_id,
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


def get_upcoming_appointment_reminders(
    user_id: int,
    reminder_hours: int = 48,
):
    """
    Return automatic reminders for confirmed appointments
    occurring within the configured reminder window.
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
            cp.specialization,
            u.full_name AS counsellor_name
        FROM appointments a
        JOIN counsellor_profiles cp
            ON cp.id = a.counsellor_profile_id
        JOIN users u
            ON u.id = cp.user_id
        WHERE
            a.user_id = %s
            AND a.status = 'confirmed'
        ORDER BY
            a.appointment_date ASC,
            a.start_time ASC
        """,
        (user_id,),
    )

    confirmed_appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    now = datetime.now()

    reminder_limit = (
        now
        + timedelta(
            hours=reminder_hours
        )
    )

    reminders = []

    for appointment in confirmed_appointments:

        appointment_datetime = (
            _build_appointment_datetime(
                appointment["appointment_date"],
                appointment["start_time"],
            )
        )

        if not (
            now
            < appointment_datetime
            <= reminder_limit
        ):
            continue

        if appointment_datetime.date() == now.date():
            reminder_text = "later today"

        elif (
            appointment_datetime.date()
            == (
                now.date()
                + timedelta(days=1)
            )
        ):
            reminder_text = "tomorrow"

        else:
            reminder_text = (
                "within the next 48 hours"
            )

        appointment[
            "formatted_start_time"
        ] = _format_start_time(
            appointment["start_time"]
        )

        appointment[
            "appointment_datetime"
        ] = appointment_datetime

        appointment[
            "reminder_text"
        ] = reminder_text

        reminders.append(
            appointment
        )

    return reminders


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
            a.availability_slot_id,
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
    Update an appointment only when it belongs to
    the logged-in counsellor.

    Rejected or cancelled appointments release their
    associated availability slot for future booking.
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
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            """
            SELECT
                a.id,
                a.status,
                a.availability_slot_id
            FROM appointments a
            JOIN counsellor_profiles cp
                ON cp.id = a.counsellor_profile_id
            WHERE
                a.id = %s
                AND cp.user_id = %s
            LIMIT 1
            FOR UPDATE
            """,
            (
                appointment_id,
                counsellor_user_id,
            ),
        )

        appointment = cursor.fetchone()

        if appointment is None:
            connection.rollback()
            return False

        cursor.execute(
            """
            UPDATE appointments
            SET status = %s
            WHERE id = %s
            """,
            (
                status,
                appointment_id,
            ),
        )

        if (
            status in {
                "rejected",
                "cancelled",
            }
            and appointment[
                "availability_slot_id"
            ] is not None
        ):
            cursor.execute(
                """
                UPDATE counsellor_availability_slots
                SET is_booked = FALSE
                WHERE id = %s
                """,
                (
                    appointment[
                        "availability_slot_id"
                    ],
                ),
            )

        connection.commit()

        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()