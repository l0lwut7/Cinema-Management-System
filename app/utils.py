import random


def generate_booking_code(cursor) -> int:
    for _ in range(20):
        code = random.randint(100000, 999999)
        cursor.execute("SELECT 1 FROM booking WHERE booking_code = %s", (code,))
        if not cursor.fetchone():
            return code
    raise RuntimeError("Could not generate unique booking code after 20 attempts")


def make_ticket_code(booking_code: int, row_letter: str, seat_number: int) -> str:
    return f"{booking_code}{row_letter}{seat_number}"
