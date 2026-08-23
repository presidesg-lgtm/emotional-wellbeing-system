from app.repositories.database import get_database_connection


def create_forum_post(
    user_id: int,
    content: str,
):
    """
    Create a new forum post for a normal user.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO forum_posts (
            user_id,
            content
        )
        VALUES (%s, %s)
        """,
        (
            user_id,
            content,
        ),
    )

    connection.commit()

    post_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return post_id


def get_visible_forum_posts():
    """
    Return visible forum posts for the normal-user community view.

    Real author names are deliberately excluded so that
    forum participation remains anonymous to other users.
    The user ID is retained only so the interface can identify
    whether a post belongs to the currently signed-in user.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            fp.id,
            fp.user_id,
            fp.content,
            fp.created_at,
            fp.updated_at
        FROM forum_posts fp
        JOIN users u
            ON u.id = fp.user_id
        WHERE
            fp.is_hidden = FALSE
            AND u.is_active = TRUE
        ORDER BY
            fp.created_at DESC,
            fp.id DESC
        """
    )

    posts = cursor.fetchall()

    cursor.close()
    connection.close()

    return posts


def get_forum_post_by_id(
    post_id: int,
):
    """
    Return one forum post by ID.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            content,
            is_hidden,
            created_at,
            updated_at
        FROM forum_posts
        WHERE id = %s
        LIMIT 1
        """,
        (post_id,),
    )

    post = cursor.fetchone()

    cursor.close()
    connection.close()

    return post


def create_forum_report(
    post_id: int,
    reported_by_user_id: int,
    reason: str,
):
    """
    Create a pending report for a forum post.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO forum_reports (
            post_id,
            reported_by_user_id,
            reason,
            status
        )
        VALUES (%s, %s, %s, 'pending')
        """,
        (
            post_id,
            reported_by_user_id,
            reason,
        ),
    )

    connection.commit()

    report_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return report_id


def has_user_reported_post(
    post_id: int,
    user_id: int,
):
    """
    Return True if the user has already reported
    the specified post.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM forum_reports
        WHERE
            post_id = %s
            AND reported_by_user_id = %s
        LIMIT 1
        """,
        (
            post_id,
            user_id,
        ),
    )

    report = cursor.fetchone()

    cursor.close()
    connection.close()

    return report is not None


def get_all_forum_reports():
    """
    Return forum reports for administrator review.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            fr.id AS report_id,
            fr.post_id,
            fr.reason,
            fr.status AS report_status,
            fr.created_at AS reported_at,
            fr.reviewed_at,
            fp.content AS post_content,
            fp.is_hidden,
            author.full_name AS author_name,
            reporter.full_name AS reporter_name,
            reporter.email AS reporter_email
        FROM forum_reports fr
        JOIN forum_posts fp
            ON fp.id = fr.post_id
        JOIN users author
            ON author.id = fp.user_id
        JOIN users reporter
            ON reporter.id = fr.reported_by_user_id
        ORDER BY
            CASE fr.status
                WHEN 'pending' THEN 1
                WHEN 'reviewed' THEN 2
                WHEN 'dismissed' THEN 3
                ELSE 4
            END,
            fr.created_at DESC
        """
    )

    reports = cursor.fetchall()

    cursor.close()
    connection.close()

    return reports


def get_all_forum_posts_for_admin():
    """
    Return all forum posts for administrator moderation,
    including hidden posts.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            fp.id,
            fp.user_id,
            fp.content,
            fp.is_hidden,
            fp.created_at,
            fp.updated_at,
            u.full_name AS author_name
        FROM forum_posts fp
        JOIN users u
            ON u.id = fp.user_id
        ORDER BY
            fp.created_at DESC,
            fp.id DESC
        """
    )

    posts = cursor.fetchall()

    cursor.close()
    connection.close()

    return posts


def set_forum_post_hidden(
    post_id: int,
    is_hidden: bool,
):
    """
    Hide or restore a forum post.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE forum_posts
        SET is_hidden = %s
        WHERE id = %s
        """,
        (
            is_hidden,
            post_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return updated


def update_forum_report_status(
    report_id: int,
    status: str,
):
    """
    Mark a forum report as reviewed or dismissed.
    """

    allowed_statuses = {
        "reviewed",
        "dismissed",
    }

    if status not in allowed_statuses:
        return False

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE forum_reports
        SET
            status = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (
            status,
            report_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return updated