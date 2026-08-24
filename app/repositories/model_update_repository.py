from app.repositories.database import get_database_connection


def get_model_update_runs():
    """
    Return model-update records for administrator review.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            mur.id,
            mur.version_label,
            mur.model_directory,
            mur.status,
            mur.is_active,
            mur.source_record_count,
            mur.notes,
            mur.created_at,
            mur.updated_at,
            mur.deployed_at,
            u.full_name AS created_by_admin_name
        FROM model_update_runs mur
        LEFT JOIN users u
            ON u.id = mur.created_by_admin_id
        ORDER BY
            mur.is_active DESC,
            mur.created_at DESC,
            mur.id DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def get_active_model_directory():
    """
    Return the directory name of the active deployed model.

    Falls back to the original validated model directory if no
    active database record exists.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT model_directory
            FROM model_update_runs
            WHERE
                is_active = TRUE
                AND status = 'deployed'
            ORDER BY deployed_at DESC, id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

    except Exception:
        # The migration may not yet exist during initial setup.
        row = None

    finally:
        cursor.close()
        connection.close()

    if row is None:
        return "selected-distilbert-emotion"

    return row["model_directory"]


def create_model_update_run(
    version_label: str,
    model_directory: str,
    source_record_count: int,
    notes,
    created_by_admin_id: int,
):
    """
    Register a candidate retrained model version.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO model_update_runs (
            version_label,
            model_directory,
            source_record_count,
            notes,
            created_by_admin_id,
            status,
            is_active
        )
        VALUES (%s, %s, %s, %s, %s, 'registered', FALSE)
        """,
        (
            version_label,
            model_directory,
            source_record_count,
            notes,
            created_by_admin_id,
        ),
    )

    connection.commit()

    run_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return run_id


def set_model_update_status(
    run_id: int,
    status: str,
):
    """
    Mark a non-active candidate as evaluated or rejected.
    """

    if status not in {
        "evaluated",
        "rejected",
    }:
        return False

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE model_update_runs
        SET status = %s
        WHERE
            id = %s
            AND is_active = FALSE
            AND status IN (
                'registered',
                'evaluated'
            )
        """,
        (
            status,
            run_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return updated


def activate_model_update(
    run_id: int,
):
    """
    Make an evaluated model the active deployed model.

    Only one model may be active at a time.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            """
            SELECT
                id,
                model_directory,
                status,
                is_active
            FROM model_update_runs
            WHERE id = %s
            LIMIT 1
            FOR UPDATE
            """,
            (run_id,),
        )

        candidate = cursor.fetchone()

        if (
            candidate is None
            or candidate["status"] != "evaluated"
        ):
            connection.rollback()
            return False

        cursor.execute(
            """
            UPDATE model_update_runs
            SET is_active = FALSE
            WHERE is_active = TRUE
            """
        )

        cursor.execute(
            """
            UPDATE model_update_runs
            SET
                status = 'deployed',
                is_active = TRUE,
                deployed_at = CURRENT_TIMESTAMP
            WHERE
                id = %s
                AND status = 'evaluated'
            """,
            (run_id,),
        )

        if cursor.rowcount != 1:
            connection.rollback()
            return False

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_candidate_retraining_rows():
    """
    Return candidate mood records without account identifiers.

    User IDs, names, emails, roles, and profile data are deliberately
    excluded. Free text is further de-identified by the service layer.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            me.id AS source_record_id,
            me.submitted_text,
            me.predicted_emotion,
            me.confidence,
            me.created_at
        FROM mood_entries me
        JOIN users u
            ON u.id = me.user_id
        WHERE u.role = 'user'
        ORDER BY me.created_at ASC, me.id ASC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows
