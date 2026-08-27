import unittest
from unittest.mock import patch

from app.repositories.appointment_repository import (
    create_appointment_from_slot,
)


class FakeCursor:

    def __init__(self, slot=None, update_rowcount=1):
        self.slot = slot
        self.update_rowcount = update_rowcount
        self.lastrowid = 101
        self.rowcount = 0
        self.execute_count = 0
        self.closed = False

    def execute(self, query, params=None):
        self.execute_count += 1

        normalized = " ".join(query.split()).upper()

        if normalized.startswith(
            "UPDATE COUNSELLOR_AVAILABILITY_SLOTS"
        ):
            self.rowcount = self.update_rowcount

    def fetchone(self):
        return self.slot

    def close(self):
        self.closed = True


class FakeConnection:

    def __init__(self, cursor):
        self._cursor = cursor
        self.transaction_started = False
        self.committed = False
        self.rollback_count = 0
        self.closed = False

    def cursor(self, dictionary=False):
        return self._cursor

    def start_transaction(self):
        self.transaction_started = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rollback_count += 1

    def close(self):
        self.closed = True


class BookingConcurrencyTests(unittest.TestCase):

    @patch(
        "app.repositories.appointment_repository."
        "get_database_connection"
    )
    def test_unavailable_slot_cannot_be_booked(
        self,
        get_connection,
    ):
        cursor = FakeCursor(slot=None)
        connection = FakeConnection(cursor)
        get_connection.return_value = connection

        appointment_id = create_appointment_from_slot(
            user_id=3,
            availability_slot_id=99,
        )

        self.assertIsNone(appointment_id)
        self.assertGreaterEqual(
            connection.rollback_count,
            1,
        )
        self.assertFalse(connection.committed)

    @patch(
        "app.repositories.appointment_repository."
        "get_database_connection"
    )
    def test_available_slot_is_committed_once(
        self,
        get_connection,
    ):
        cursor = FakeCursor(
            slot={
                "id": 44,
                "counsellor_profile_id": 2,
                "slot_date": "2026-08-30",
                "start_time": "16:20:00",
                "is_booked": False,
            },
            update_rowcount=1,
        )
        connection = FakeConnection(cursor)
        get_connection.return_value = connection

        appointment_id = create_appointment_from_slot(
            user_id=3,
            availability_slot_id=44,
        )

        self.assertEqual(appointment_id, 101)
        self.assertTrue(connection.transaction_started)
        self.assertTrue(connection.committed)
        self.assertEqual(connection.rollback_count, 0)

    @patch(
        "app.repositories.appointment_repository."
        "get_database_connection"
    )
    def test_failed_atomic_slot_update_rolls_back(
        self,
        get_connection,
    ):
        cursor = FakeCursor(
            slot={
                "id": 44,
                "counsellor_profile_id": 2,
                "slot_date": "2026-08-30",
                "start_time": "16:20:00",
                "is_booked": False,
            },
            update_rowcount=0,
        )
        connection = FakeConnection(cursor)
        get_connection.return_value = connection

        appointment_id = create_appointment_from_slot(
            user_id=6,
            availability_slot_id=44,
        )

        self.assertIsNone(appointment_id)
        self.assertGreaterEqual(
            connection.rollback_count,
            1,
        )
        self.assertFalse(connection.committed)


if __name__ == "__main__":
    unittest.main()
