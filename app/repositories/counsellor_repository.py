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


def get_all_counsellors_for_admin():
    """
    Return all counsellor accounts and profiles,
    including inactive or unavailable counsellors.
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
            u.is_active,
            cp.specialization,
            cp.qualifications,
            cp.bio,
            cp.years_experience,
            cp.is_available,
            u.created_at,
            u.updated_at
        FROM counsellor_profiles cp
        JOIN users u
            ON u.id = cp.user_id
        WHERE u.role = 'counsellor'
        ORDER BY u.full_name ASC, cp.id ASC
        """
    )

    counsellors = cursor.fetchall()

    cursor.close()
    connection.close()

    return counsellors


def create_counsellor_account(
    full_name: str,
    email: str,
    password_hash: str,
    specialization: str,
    qualifications,
    bio,
    years_experience: int,
    is_available: bool,
):
    """
    Create a counsellor login and profile in one transaction.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                email,
                password_hash,
                role,
                is_active
            )
            VALUES (%s, %s, %s, 'counsellor', TRUE)
            """,
            (
                full_name,
                email,
                password_hash,
            ),
        )

        counsellor_user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO counsellor_profiles (
                user_id,
                specialization,
                qualifications,
                bio,
                years_experience,
                is_available
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                counsellor_user_id,
                specialization,
                qualifications,
                bio,
                years_experience,
                is_available,
            ),
        )

        profile_id = cursor.lastrowid
        connection.commit()

        return profile_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def update_counsellor_account(
    profile_id: int,
    full_name: str,
    email: str,
    specialization: str,
    qualifications,
    bio,
    years_experience: int,
    is_available: bool,
):
    """
    Update counsellor account and profile information
    together in one transaction.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            """
            SELECT cp.user_id
            FROM counsellor_profiles cp
            JOIN users u
                ON u.id = cp.user_id
            WHERE
                cp.id = %s
                AND u.role = 'counsellor'
            LIMIT 1
            FOR UPDATE
            """,
            (profile_id,),
        )

        record = cursor.fetchone()

        if record is None:
            connection.rollback()
            return False

        cursor.execute(
            """
            UPDATE users
            SET
                full_name = %s,
                email = %s
            WHERE
                id = %s
                AND role = 'counsellor'
            """,
            (
                full_name,
                email,
                record['user_id'],
            ),
        )

        cursor.execute(
            """
            UPDATE counsellor_profiles
            SET
                specialization = %s,
                qualifications = %s,
                bio = %s,
                years_experience = %s,
                is_available = %s
            WHERE id = %s
            """,
            (
                specialization,
                qualifications,
                bio,
                years_experience,
                is_available,
                profile_id,
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


def get_user_counsellor_assignments():
    """
    Return current user-to-counsellor assignments.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            uca.id,
            uca.user_id,
            u.full_name AS user_name,
            u.email AS user_email,
            uca.counsellor_profile_id,
            cu.full_name AS counsellor_name,
            cp.specialization,
            cp.is_available AS counsellor_is_available,
            cu.is_active AS counsellor_is_active,
            uca.support_requirement,
            uca.assigned_at,
            uca.updated_at
        FROM user_counsellor_assignments uca
        JOIN users u
            ON u.id = uca.user_id
        JOIN counsellor_profiles cp
            ON cp.id = uca.counsellor_profile_id
        JOIN users cu
            ON cu.id = cp.user_id
        ORDER BY u.full_name ASC
        """
    )

    assignments = cursor.fetchall()

    cursor.close()
    connection.close()

    return assignments


def assign_counsellor_to_user(
    user_id: int,
    counsellor_profile_id: int,
    assigned_by_admin_id: int,
    support_requirement,
):
    """
    Create or replace the current counsellor assignment
    for one active normal user.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE
                id = %s
                AND role = 'user'
                AND is_active = TRUE
            LIMIT 1
            """,
            (user_id,),
        )

        if cursor.fetchone() is None:
            connection.rollback()
            return False

        cursor.execute(
            """
            SELECT cp.id
            FROM counsellor_profiles cp
            JOIN users u
                ON u.id = cp.user_id
            WHERE
                cp.id = %s
                AND u.role = 'counsellor'
                AND u.is_active = TRUE
            LIMIT 1
            """,
            (counsellor_profile_id,),
        )

        if cursor.fetchone() is None:
            connection.rollback()
            return False

        cursor.execute(
            """
            INSERT INTO user_counsellor_assignments (
                user_id,
                counsellor_profile_id,
                assigned_by_admin_id,
                support_requirement
            )
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                counsellor_profile_id = VALUES(counsellor_profile_id),
                assigned_by_admin_id = VALUES(assigned_by_admin_id),
                support_requirement = VALUES(support_requirement),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                counsellor_profile_id,
                assigned_by_admin_id,
                support_requirement,
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


def remove_counsellor_assignment(user_id: int):
    """
    Remove the current counsellor assignment for a user.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM user_counsellor_assignments
        WHERE user_id = %s
        """,
        (user_id,),
    )

    connection.commit()
    removed = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return removed
