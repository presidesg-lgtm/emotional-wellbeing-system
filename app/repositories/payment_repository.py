from app.repositories.database import get_database_connection


def get_appointment_for_payment(
    appointment_id: int,
    user_id: int,
):
    """
    Return an appointment only when it belongs to
    the specified user.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            a.id,
            a.user_id,
            a.appointment_date,
            a.start_time,
            a.status,
            cp.id AS counsellor_profile_id,
            u.full_name AS counsellor_name,
            cp.specialization
        FROM appointments a
        JOIN counsellor_profiles cp
            ON cp.id = a.counsellor_profile_id
        JOIN users u
            ON u.id = cp.user_id
        WHERE
            a.id = %s
            AND a.user_id = %s
        LIMIT 1
        """,
        (
            appointment_id,
            user_id,
        ),
    )

    appointment = cursor.fetchone()

    cursor.close()
    connection.close()

    return appointment


def find_payment_proof_by_appointment(
    appointment_id: int,
):
    """
    Return an existing payment proof for an appointment,
    or None when no proof has been submitted.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            appointment_id,
            user_id,
            original_filename,
            stored_filename,
            status,
            admin_note,
            submitted_at,
            reviewed_at
        FROM payment_proofs
        WHERE appointment_id = %s
        LIMIT 1
        """,
        (appointment_id,),
    )

    payment_proof = cursor.fetchone()

    cursor.close()
    connection.close()

    return payment_proof


def create_payment_proof(
    appointment_id: int,
    user_id: int,
    original_filename: str,
    stored_filename: str,
):
    """
    Store payment-proof metadata with pending status.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO payment_proofs (
            appointment_id,
            user_id,
            original_filename,
            stored_filename,
            status
        )
        VALUES (%s, %s, %s, %s, 'pending')
        """,
        (
            appointment_id,
            user_id,
            original_filename,
            stored_filename,
        ),
    )

    connection.commit()

    payment_proof_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return payment_proof_id


def get_payment_proofs_by_user(
    user_id: int,
):
    """
    Return payment-proof records belonging to one user.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            pp.id,
            pp.appointment_id,
            pp.original_filename,
            pp.status,
            pp.admin_note,
            pp.submitted_at,
            pp.reviewed_at
        FROM payment_proofs pp
        WHERE pp.user_id = %s
        ORDER BY pp.submitted_at DESC
        """,
        (user_id,),
    )

    payment_proofs = cursor.fetchall()

    cursor.close()
    connection.close()

    return payment_proofs


def get_all_payment_proofs():
    """
    Return payment proofs for administrator review
    together with appointment and account information.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            pp.id,
            pp.appointment_id,
            pp.user_id,
            pp.original_filename,
            pp.stored_filename,
            pp.status,
            pp.admin_note,
            pp.submitted_at,
            pp.reviewed_at,
            user_account.full_name AS user_name,
            user_account.email AS user_email,
            counsellor_account.full_name AS counsellor_name,
            a.appointment_date,
            a.start_time
        FROM payment_proofs pp
        JOIN appointments a
            ON a.id = pp.appointment_id
        JOIN users user_account
            ON user_account.id = pp.user_id
        JOIN counsellor_profiles cp
            ON cp.id = a.counsellor_profile_id
        JOIN users counsellor_account
            ON counsellor_account.id = cp.user_id
        ORDER BY
            CASE pp.status
                WHEN 'pending' THEN 1
                WHEN 'verified' THEN 2
                WHEN 'rejected' THEN 3
                ELSE 4
            END,
            pp.submitted_at DESC
        """
    )

    payment_proofs = cursor.fetchall()

    cursor.close()
    connection.close()

    return payment_proofs


def get_payment_proof_by_id(
    payment_proof_id: int,
):
    """
    Return one payment-proof record by ID.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            appointment_id,
            user_id,
            original_filename,
            stored_filename,
            status,
            admin_note,
            submitted_at,
            reviewed_at
        FROM payment_proofs
        WHERE id = %s
        LIMIT 1
        """,
        (payment_proof_id,),
    )

    payment_proof = cursor.fetchone()

    cursor.close()
    connection.close()

    return payment_proof


def review_payment_proof(
    payment_proof_id: int,
    status: str,
    admin_note: str | None = None,
):
    """
    Mark a payment proof as verified or rejected
    and record the review time.
    """

    allowed_statuses = {
        "verified",
        "rejected",
    }

    if status not in allowed_statuses:
        return False

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE payment_proofs
        SET
            status = %s,
            admin_note = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (
            status,
            admin_note,
            payment_proof_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return updated