import sqlite3

class Database:
    def __init__(self, db_path="databases/test.db"):
        self.db_path = db_path
        self.init_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nursing_home_name TEXT NOT NULL,
                location TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                service_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                contact_email TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                special_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        cursor.execute("PRAGMA table_info(Bookings)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'booking_date' not in columns:
            cursor.execute("ALTER TABLE Bookings ADD COLUMN booking_date TEXT")
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE Bookings ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        conn.close()

    def add_booking(self, nursing_home_name, location, booking_date, booking_time,
                    service_type, contact_email, contact_phone, special_notes):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Bookings (
                nursing_home_name, location, booking_date, booking_time,
                service_type, contact_email, contact_phone, special_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nursing_home_name, location, booking_date, booking_time,
              service_type, contact_email, contact_phone, special_notes))
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return booking_id

    def get_all_bookings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bookings ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_booking_by_id(self, booking_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = ?", (booking_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def get_booked_slots(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT booking_date, booking_time FROM Bookings WHERE status != 'declined'")
        rows = cursor.fetchall()
        conn.close()
        return {(row[0], row[1]) for row in rows}

    def get_bookings(self, status=None, search=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        base_query = "SELECT * FROM Bookings"
        params = []
        filters = []
        if status:
            filters.append("status = ?")
            params.append(status)
        if search:
            filters.append("(nursing_home_name LIKE ? OR location LIKE ? OR service_type LIKE ? OR contact_email LIKE ?)")
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])
        if filters:
            base_query += " WHERE " + " AND ".join(filters)
        base_query += " ORDER BY created_at DESC"
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_booking_status(self, booking_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Bookings SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (status, booking_id))
        conn.commit()
        conn.close()
