from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from werkzeug.security import check_password_hash
from app.db import get_db_connection
from app.utils import generate_booking_code, make_ticket_code
from datetime import datetime, timedelta

staff_bp = Blueprint("staff", __name__)


def _infer_emoji(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("popcorn",)):                                      return "🍿"
    if any(k in n for k in ("cola", "soda", "pepsi", "coke", "sprite", "fanta", "lemonade", "juice")): return "🥤"
    if any(k in n for k in ("water", "still", "sparkling")):                   return "💧"
    if any(k in n for k in ("coffee", "latte", "cappuccino", "espresso", "americano")): return "☕"
    if any(k in n for k in ("tea", "chai")):                                   return "🍵"
    if any(k in n for k in ("beer", "ale", "lager")):                          return "🍺"
    if any(k in n for k in ("wine", "champagne")):                             return "🍷"
    if any(k in n for k in ("nacho", "chip", "crisp")):                        return "🌮"
    if any(k in n for k in ("hot dog", "hotdog", "sausage")):                  return "🌭"
    if any(k in n for k in ("burger", "sandwich")):                            return "🍔"
    if any(k in n for k in ("pizza",)):                                        return "🍕"
    if any(k in n for k in ("pretzel",)):                                      return "🥨"
    if any(k in n for k in ("chocolate", "choc", "candy", "sweet", "truffle")): return "🍫"
    if any(k in n for k in ("ice cream", "icecream", "gelato", "sorbet")):     return "🍦"
    if any(k in n for k in ("donut", "doughnut")):                             return "🍩"
    if any(k in n for k in ("cookie", "biscuit")):                             return "🍪"
    if any(k in n for k in ("cake", "brownie", "muffin")):                     return "🎂"
    return "🍽️"


@staff_bp.route("/staff/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "error")
            return render_template("staff/login.html")

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT u.user_id, u.first_name, u.last_name, u.password_hash,
                       e.role, e.theater_id, e.auth_level
                FROM user u
                JOIN employee e ON u.user_id = e.user_id
                WHERE u.email = %s AND e.account_status = 'Active'
                """,
                (email,)
            )
            employee = cursor.fetchone()

            if employee and check_password_hash(employee["password_hash"], password):
                # Ensure a CUSTOMER row exists so POS bookings can reference this user_id
                cursor.execute(
                    "SELECT user_id FROM customer WHERE user_id = %s",
                    (employee["user_id"],)
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO customer (user_id) VALUES (%s)",
                        (employee["user_id"],)
                    )
                    conn.commit()

                name = f"{employee['first_name']} {employee['last_name']}"
                initials = (employee["first_name"][0] + employee["last_name"][0]).upper()

                session["staff_id"] = employee["user_id"]
                session["staff_theater_id"] = employee["theater_id"]
                session["staff_name"] = name
                session["staff_role"] = employee["role"]
                session["staff_initials"] = initials

                return redirect(url_for("staff.terminal"))
            else:
                flash("Invalid email or password", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template("staff/login.html")


@staff_bp.route("/staff/logout", strict_slashes=False)
def logout():
    for key in ["staff_id", "staff_theater_id", "staff_name", "staff_role", "staff_initials"]:
        session.pop(key, None)
    return redirect(url_for("staff.login"))


@staff_bp.route("/staff/terminal", strict_slashes=False)
def terminal():
    if "staff_id" not in session:
        return redirect(url_for("staff.login"))

    theater_id = session.get("staff_theater_id")

    conn = get_db_connection()
    screenings = []
    consumables = []

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            if theater_id is not None:
                # Use DATE() comparison so today's screenings show even if start_time has passed
                cursor.execute(
                    """
                    SELECT s.screening_id, m.title AS movie_name, s.saloon_number,
                           s.start_time, s.base_price, s.is_subtitled, m.poster_url
                    FROM screening s
                    JOIN movie m ON s.movie_id = m.movie_id
                    WHERE s.theater_id = %s AND DATE(s.start_time) >= CURDATE()
                    ORDER BY s.start_time
                    LIMIT 50
                    """,
                    (theater_id,)
                )
                screenings = cursor.fetchall()

            cursor.execute(
                "SELECT consumable_id, name, unit_price, stock_quantity FROM consumable ORDER BY name"
            )
            consumables = [{**c, "emoji": _infer_emoji(c["name"])} for c in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    staff = {
        "name": session.get("staff_name", "Staff"),
        "role": session.get("staff_role", "Staff"),
        "initials": session.get("staff_initials", "S"),
        "terminal": f"T-{theater_id or '?'}",
    }

    return render_template(
        "staff/terminal.html",
        screenings=screenings,
        consumables=consumables,
        staff=staff,
    )


@staff_bp.route("/staff/seats/<int:screening_id>", strict_slashes=False)
def get_seats(screening_id):
    if "staff_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    theater_id = session.get("staff_theater_id")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT screening_id, saloon_number, base_price
            FROM screening
            WHERE screening_id = %s AND theater_id = %s
            """,
            (screening_id, theater_id)
        )
        screening = cursor.fetchone()
        if not screening:
            return jsonify({"error": "Screening not found"}), 404

        saloon_number = screening["saloon_number"]

        cursor.execute(
            """
            SELECT row_letter, number
            FROM seat
            WHERE theater_id = %s AND saloon_number = %s
            ORDER BY row_letter, number
            """,
            (theater_id, saloon_number)
        )
        all_seats = cursor.fetchall()

        cursor.execute(
            "SELECT row_letter, seat_number FROM ticket WHERE screening_id = %s",
            (screening_id,)
        )
        occupied_set = {(r["row_letter"], r["seat_number"]) for r in cursor.fetchall()}

        rows = {}
        for seat in all_seats:
            row = seat["row_letter"]
            if row not in rows:
                rows[row] = []
            rows[row].append({
                "number": seat["number"],
                "occupied": (row, seat["number"]) in occupied_set,
            })

        return jsonify({
            "rows": rows,
            "base_price": float(screening["base_price"]),
        })
    finally:
        cursor.close()
        conn.close()


@staff_bp.route("/staff/checkout", methods=["POST"], strict_slashes=False)
def checkout():
    if "staff_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    screening_id = data.get("screening_id")
    seats = data.get("seats", [])
    consumables_data = data.get("consumables", [])

    if not screening_id or not seats:
        return jsonify({"error": "Missing screening or seats"}), 400

    theater_id = session.get("staff_theater_id")
    user_id = session.get("staff_id")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        # ── Read-only validation (part of the implicit transaction; no writes yet) ──

        cursor.execute(
            """
            SELECT screening_id, saloon_number, base_price
            FROM screening
            WHERE screening_id = %s AND theater_id = %s
            """,
            (screening_id, theater_id)
        )
        screening = cursor.fetchone()
        if not screening:
            return jsonify({"error": "Screening not found"}), 404

        saloon_number = screening["saloon_number"]
        base_price    = float(screening["base_price"])

        for seat in seats:
            cursor.execute(
                """
                SELECT ticket_id FROM ticket
                WHERE screening_id = %s AND row_letter = %s AND seat_number = %s
                """,
                (screening_id, seat["row"], seat["number"])
            )
            if cursor.fetchone():
                return jsonify({"error": f"Seat {seat['row']}{seat['number']} is already taken"}), 409

        ticket_total      = base_price * len(seats)
        consumable_total  = 0.0
        consumable_details = []

        for c in consumables_data:
            cursor.execute(
                "SELECT consumable_id, name, unit_price, stock_quantity FROM consumable WHERE consumable_id = %s",
                (c["id"],)
            )
            cons_row = cursor.fetchone()
            if not cons_row:
                return jsonify({"error": f"Consumable {c['id']} not found"}), 404
            qty = int(c["quantity"])
            if cons_row["stock_quantity"] < qty:
                return jsonify({"error": f"Insufficient stock for {cons_row['name']}"}), 409
            consumable_total += float(cons_row["unit_price"]) * qty
            consumable_details.append({"id": cons_row["consumable_id"], "qty": qty})

        total_amount = ticket_total + consumable_total

        method_label = {
            "cash":   "POS Cash",
            "card":   "POS Card",
            "mobile": "POS Mobile",
        }.get(data.get("method", "cash"), "POS Cash")

        # ── Writes — no conn.start_transaction(); the implicit transaction
        #    (autocommit=False by default) already covers everything above.
        #    Calling start_transaction() on top of it raises
        #    "Transaction already in progress". ──

        booking_code = generate_booking_code(cursor)
        cursor.execute(
            "INSERT INTO booking (user_id, total_amount, booking_code, screening_id) VALUES (%s, %s, %s, %s)",
            (user_id, total_amount, booking_code, screening_id)
        )
        booking_id = cursor.lastrowid

        ticket_codes = []
        for seat in seats:
            tc = make_ticket_code(booking_code, seat["row"], seat["number"])
            cursor.execute(
                """
                INSERT INTO ticket
                    (booking_id, screening_id, theater_id, saloon_number,
                     row_letter, seat_number, ticket_type, ticket_code)
                VALUES (%s, %s, %s, %s, %s, %s, 'Standard', %s)
                """,
                (booking_id, screening_id, theater_id, saloon_number,
                 seat["row"], seat["number"], tc)
            )
            ticket_codes.append(tc)

        for c in consumable_details:
            cursor.execute(
                "INSERT INTO booking_consumable (booking_id, consumable_id, quantity) VALUES (%s, %s, %s)",
                (booking_id, c["id"], c["qty"])
            )
            cursor.execute(
                "UPDATE consumable SET stock_quantity = stock_quantity - %s WHERE consumable_id = %s",
                (c["qty"], c["id"])
            )

        cursor.execute(
            "INSERT INTO payment (booking_id, method, status) VALUES (%s, %s, 'Completed')",
            (booking_id, method_label)
        )

        conn.commit()
        return jsonify({"success": True, "booking_id": booking_id, "booking_code": booking_code, "ticket_ids": ticket_codes})

    except Exception as e:
        print(f"CHECKOUT ERROR: {str(e)}")
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass


@staff_bp.route("/staff/validate_booking", methods=["POST"], strict_slashes=False)
def validate_booking():
    """Scan a 6-digit booking_code at the entrance; marks all tickets as scanned on success."""
    if "staff_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    raw_code = data.get("booking_code") if data else None

    try:
        booking_code = int(str(raw_code).strip())
    except (ValueError, TypeError):
        return jsonify({"valid": False, "reason": "Invalid format — must be a 6-digit number"}), 200

    theater_id = session.get("staff_theater_id")

    conn = get_db_connection()
    if not conn:
        return jsonify({"valid": False, "reason": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Verify the booking belongs to this theater via the screening snapshot
        cursor.execute(
            """
            SELECT b.booking_id, b.booking_code, m.title AS movie_name,
                   s.start_time, p.status AS payment_status
            FROM booking b
            JOIN screening s ON b.screening_id = s.screening_id
            JOIN movie m ON s.movie_id = m.movie_id
            LEFT JOIN payment p ON b.booking_id = p.booking_id
            WHERE b.booking_code = %s AND s.theater_id = %s
            """,
            (booking_code, theater_id)
        )
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"valid": False, "reason": "Booking not found for this theater"}), 200

        if booking["payment_status"] == "Refunded":
            return jsonify({"valid": False, "reason": "Booking has been refunded"}), 200

        # Fetch all remaining (non-refunded) tickets
        cursor.execute(
            """
            SELECT ticket_id, scanned_at, row_letter, seat_number
            FROM ticket
            WHERE booking_id = %s
            ORDER BY row_letter, seat_number
            """,
            (booking["booking_id"],)
        )
        tickets = cursor.fetchall()

        if not tickets:
            return jsonify({"valid": False, "reason": "No active tickets found — may be fully refunded"}), 200

        # Already scanned check
        scanned_tickets = [t for t in tickets if t["scanned_at"]]
        if scanned_tickets:
            scan_time = scanned_tickets[0]["scanned_at"].strftime("%H:%M")
            return jsonify({"valid": False, "reason": f"Already scanned at {scan_time}"}), 200

        # Mark all unscanned tickets
        cursor.execute(
            "UPDATE ticket SET scanned_at = NOW() WHERE booking_id = %s AND scanned_at IS NULL",
            (booking["booking_id"],)
        )
        conn.commit()

        seats = ", ".join(f"{t['row_letter']}{t['seat_number']}" for t in tickets)
        return jsonify({
            "valid":        True,
            "booking_code": booking["booking_code"],
            "movie":        booking["movie_name"],
            "seats":        seats,
            "ticket_count": len(tickets),
        }), 200

    except Exception as e:
        print(f"VALIDATE BOOKING ERROR: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"valid": False, "reason": "Server error"}), 500

    finally:
        cursor.close()
        conn.close()


@staff_bp.route("/staff/validate_ticket", methods=["POST"], strict_slashes=False)
def validate_ticket():
    if "staff_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    ticket_code = (data.get("ticket_code") or "").strip().upper() if data else ""

    if not ticket_code:
        return jsonify({"error": "Missing ticket_code"}), 400

    theater_id = session.get("staff_theater_id")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT t.ticket_id, t.scanned_at, t.row_letter, t.seat_number, t.saloon_number,
                   s.start_time, m.title AS movie_name
            FROM ticket t
            JOIN screening s ON t.screening_id = s.screening_id
            JOIN movie m ON s.movie_id = m.movie_id
            WHERE t.ticket_code = %s AND t.theater_id = %s
            """,
            (ticket_code, theater_id)
        )
        ticket = cursor.fetchone()

        if not ticket:
            return jsonify({"valid": False, "reason": "Ticket not found or does not belong to this theater"}), 200

        if ticket["scanned_at"]:
            scanned = ticket["scanned_at"].strftime("%H:%M")
            return jsonify({"valid": False, "reason": f"Already scanned at {scanned}"}), 200

        if ticket["start_time"] < datetime.now() - timedelta(hours=2):
            return jsonify({"valid": False, "reason": "Screening has already ended"}), 200

        cursor.execute(
            "UPDATE ticket SET scanned_at = NOW() WHERE ticket_id = %s",
            (ticket["ticket_id"],)
        )
        conn.commit()

        return jsonify({
            "valid": True,
            "movie": ticket["movie_name"],
            "seat": f"{ticket['row_letter']}{ticket['seat_number']}",
            "saloon": ticket["saloon_number"],
        })
    finally:
        cursor.close()
        conn.close()


@staff_bp.route("/staff/booking-tickets/<int:booking_code>", strict_slashes=False)
def get_booking_tickets(booking_code):
    """Step 1 of the staff refund flow: look up a booking by its 6-digit code."""
    if "staff_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    theater_id = session.get("staff_theater_id")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT b.booking_id, b.booking_code, b.total_amount,
                   m.title AS movie_name, s.start_time, s.base_price
            FROM booking b
            JOIN screening s ON b.screening_id = s.screening_id
            JOIN movie m ON s.movie_id = m.movie_id
            WHERE b.booking_code = %s AND s.theater_id = %s
            """,
            (booking_code, theater_id)
        )
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"error": "Booking not found for this theater"}), 404

        cursor.execute(
            """
            SELECT ticket_code, row_letter, seat_number
            FROM ticket
            WHERE booking_id = %s
            ORDER BY row_letter, seat_number
            """,
            (booking["booking_id"],)
        )
        raw_tickets = cursor.fetchall()

        tickets = [
            {
                "ticket_code": t["ticket_code"],
                "seat": f"{t['row_letter']}{t['seat_number']}",
            }
            for t in raw_tickets
        ]

        start = booking["start_time"]
        return jsonify({
            "booking_code":  booking["booking_code"],
            "movie":         booking["movie_name"],
            "start_display": start.strftime("%b %d, %Y • %I:%M %p").lstrip("0") if hasattr(start, "strftime") else str(start),
            "total_amount":  float(booking["total_amount"]),
            "base_price":    float(booking["base_price"]),
            "tickets":       tickets,
        })
    finally:
        cursor.close()
        conn.close()


@staff_bp.route("/staff/process_refund", methods=["POST"], strict_slashes=False)
def process_refund():
    """Step 2 of the staff refund flow: delete selected tickets, update booking total."""
    if "staff_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    ticket_codes = data.get("ticket_codes", []) if data else []

    if not ticket_codes:
        return jsonify({"error": "No ticket codes provided"}), 400

    theater_id = session.get("staff_theater_id")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        # Validate all tickets belong to this theater and get booking/price info
        placeholders = ", ".join(["%s"] * len(ticket_codes))
        cursor.execute(
            f"""
            SELECT t.ticket_id, t.ticket_code, t.booking_id,
                   t.row_letter, t.seat_number, s.base_price
            FROM ticket t
            JOIN screening s ON t.screening_id = s.screening_id
            WHERE t.ticket_code IN ({placeholders}) AND t.theater_id = %s
            """,
            (*ticket_codes, theater_id)
        )
        validated = cursor.fetchall()

        if len(validated) != len(ticket_codes):
            return jsonify({"error": "One or more tickets not found or not in this theater"}), 404

        booking_id  = validated[0]["booking_id"]
        base_price  = float(validated[0]["base_price"])
        refund_amount = base_price * len(validated)
        refunded_seats = [f"{t['row_letter']}{t['seat_number']}" for t in validated]

        # Delete the selected tickets (frees the seats immediately)
        ticket_ids_to_delete = [t["ticket_id"] for t in validated]
        del_placeholders = ", ".join(["%s"] * len(ticket_ids_to_delete))
        cursor.execute(
            f"DELETE FROM ticket WHERE ticket_id IN ({del_placeholders})",
            ticket_ids_to_delete
        )

        # Recalculate booking total
        cursor.execute(
            "UPDATE booking SET total_amount = GREATEST(0, total_amount - %s) WHERE booking_id = %s",
            (refund_amount, booking_id)
        )

        # Check whether any tickets remain
        cursor.execute(
            "SELECT COUNT(*) AS remaining FROM ticket WHERE booking_id = %s",
            (booking_id,)
        )
        remaining = cursor.fetchone()["remaining"]

        if remaining == 0:
            cursor.execute(
                "UPDATE payment SET status = 'Refunded' WHERE booking_id = %s",
                (booking_id,)
            )

        conn.commit()

        return jsonify({
            "success":        True,
            "refunded_seats": refunded_seats,
            "refunded_count": len(refunded_seats),
            "fully_refunded": remaining == 0,
        })

    except Exception as e:
        print(f"STAFF REFUND ERROR: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
