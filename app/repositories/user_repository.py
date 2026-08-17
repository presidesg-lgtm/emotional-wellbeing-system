from app.repositories.database import get_database_connection


def find_user_by_email(email: str):
    """
    Return a user record matching the supplied email address,
    or None when no user exists.
    """

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            full_name,
            email,
            password_hash,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE email = %s
        LIMIT 1
        """,
        (email,),
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def create_user(
    full_name: str,
    email: str,
    password_hash: str,
    role: str = "user",
):
    """
    Insert a new user into the database.
    """

    connection = get_database_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            full_name,
            email,
            password_hash,
            role
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            full_name,
            email,
            password_hash,
            role,
        ),
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return user_id