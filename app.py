import csv
import io
import os
import ssl
import smtplib
import flask
from flask import render_template, request, redirect, url_for, session, jsonify, abort
from datetime import date, datetime
from calender_system import CalendarSystem
from database import Database
from functools import wraps


calendar_system = CalendarSystem(num_weeks=8)
db = Database('databases/test.db')

app = flask.Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'UngeToner4Ever')
SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = os.environ.get('SMTP_PORT')
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'no-reply@ungetoner.dk')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', EMAIL_FROM)
ALLOWED_TIMES = [f"{h}:00" for h in range(12, 20)]


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about_fun():
    return  render_template("about.html")

def send_email(recipient, subject, body):
    missing_setup = not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASSWORD)
    if missing_setup:
        print("Email disabled: missing SMTP configuration")
        print(f"To: {recipient}\nSubject: {subject}\n\n{body}\n")
        return False

    message = f"From: {EMAIL_FROM}\r\nTo: {recipient}\r\nSubject: {subject}\r\n\r\n{body}"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, int(SMTP_PORT), context=context) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, recipient, message)
    return True


def format_booking(row):
    return {
        'booking_id': row[0],
        'nursing_home_name': row[1],
        'location': row[2],
        'booking_date': row[3],
        'booking_time': row[4],
        'service_type': row[5],
        'status': row[6],
        'contact_email': row[7],
        'contact_phone': row[8],
        'special_notes': row[9],
        'created_at': row[10],
        'updated_at': row[11]
    }


def build_availability():
    booked_slots = db.get_booked_slots()
    availability = {}
    for slot_date, slots in calendar_system.calendar.items():
        slot_date_str = slot_date.isoformat()
        availability[slot_date] = {}
        for hour in slots.keys():
            time_label = f"{hour}:00"
            availability[slot_date][hour] = (slot_date_str, time_label) not in booked_slots
    return availability


def notify_new_booking(booking):
    subject = f"Unge Toner booking received — #{booking['booking_id']}"
    body = (
        f"Hello {booking['nursing_home_name']},\n\n"
        f"We have received your booking request for {booking['booking_date']} at {booking['booking_time']}.")
    send_email(booking['contact_email'], subject, body)

    admin_subject = f"New booking request #{booking['booking_id']}"
    admin_body = (
        f"New booking received:\n"
        f"Nursing home: {booking['nursing_home_name']}\n"
        f"Location: {booking['location']}\n"
        f"Date & time: {booking['booking_date']} {booking['booking_time']}\n"
        f"Service: {booking['service_type']}\n"
        f"Email: {booking['contact_email']}\n"
        f"Phone: {booking['contact_phone']}\n"
        f"Notes: {booking['special_notes'] or 'None'}\n"
        f"Status: {booking['status']}\n"
    )
    send_email(ADMIN_EMAIL, admin_subject, admin_body)


def notify_status_change(booking):
    subject = f"Unge Toner booking update — #{booking['booking_id']}"
    body = (
        f"Hello {booking['nursing_home_name']},\n\n"
        f"Your booking for {booking['booking_date']} at {booking['booking_time']} has been {booking['status']}.\n\n"
        f"If you have questions, reply to this email.\n"
    )
    send_email(booking['contact_email'], subject, body)


@app.route("/schedule", methods=['GET', 'POST'])
def schedule_fun():
    availability = build_availability()
    selected_date = ''
    selected_time = ''
    form_data = {
        'nursing_home': '',
        'location': '',
        'service_type': '',
        'contact_email': '',
        'contact_phone': '',
        'notes': ''
    }

    if request.method == 'POST':
        nursing_home = request.form.get('nursing_home', '').strip()
        location = request.form.get('location', '').strip()
        booking_date = request.form.get('booking_date', '').strip()
        booking_time = request.form.get('booking_time', '').strip()
        service_type = request.form.get('service_type', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        notes = request.form.get('notes', '').strip()

        selected_date = booking_date
        selected_time = booking_time
        form_data = {
            'nursing_home': nursing_home,
            'location': location,
            'service_type': service_type,
            'contact_email': contact_email,
            'contact_phone': contact_phone,
            'notes': notes
        }

        errors = []
        if not nursing_home:
            errors.append("Nursing home name is required")
        if not location:
            errors.append("Location is required")
        if not booking_date:
            errors.append("Booking date is required")
        if not booking_time:
            errors.append("Booking time is required")
        if booking_time and booking_time not in ALLOWED_TIMES:
            errors.append("Please choose a time between 12:00 and 19:00")
        if booking_date:
            try:
                selected_date_obj = date.fromisoformat(booking_date)
                if selected_date_obj not in availability:
                    errors.append("Selected date is not available")
            except ValueError:
                errors.append("Selected date is invalid")
        if not service_type:
            errors.append("Service type is required")
        if not contact_email or '@' not in contact_email:
            errors.append("Valid email is required")
        if not contact_phone or len(contact_phone) < 8:
            errors.append("Valid phone number is required")

        if not errors and booking_date and booking_time:
            if (booking_date, booking_time) not in db.get_booked_slots():
                pass
            else:
                errors.append("That time slot is already booked. Please choose another time.")

        if errors:
            return render_template(
                "schedule.html",
                availability=availability,
                errors=errors,
                selected_date=selected_date,
                selected_time=selected_time,
                form_data=form_data
            )

        booking_id = db.add_booking(
            nursing_home_name=nursing_home,
            location=location,
            booking_date=booking_date,
            booking_time=booking_time,
            service_type=service_type,
            contact_email=contact_email,
            contact_phone=contact_phone,
            special_notes=notes
        )

        booking = format_booking(db.get_booking_by_id(booking_id))
        notify_new_booking(booking)
        return render_template("booking_success.html", booking_id=booking_id)

    return render_template("schedule.html", availability=availability)

@app.route("/contact")
def contact_fun():
    return  render_template("contact.html")

@app.route("/programme")
def programme_fun():
    return render_template("programme.html")

@app.route("/statistics")
def statistics_fun():
    return  render_template("statistics.html")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        error = 'Incorrect password'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    rows = db.get_bookings(status=status_filter if status_filter and status_filter != 'all' else None, search=search if search else None)
    bookings = [format_booking(row) for row in rows]
    return render_template('admin_dashboard.html', bookings=bookings, status_filter=status_filter, search=search)

@app.route('/admin/booking/<int:booking_id>')
@admin_required
def admin_booking_detail(booking_id):
    row = db.get_booking_by_id(booking_id)
    if not row:
        abort(404)
    booking = format_booking(row)
    return render_template('admin_booking_detail.html', booking=booking)

@app.route('/admin/bookings/export')
@admin_required
def admin_export_bookings():
    rows = db.get_bookings()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Booking ID', 'Nursing Home', 'Location', 'Booking Date', 'Booking Time', 'Service Type', 'Status', 'Email', 'Phone', 'Notes', 'Created At', 'Updated At'])
    for row in rows:
        writer.writerow(row)
    response = flask.make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=unge_toner_bookings.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/admin/booking/<int:booking_id>/status', methods=['POST'])
@admin_required
def admin_update_status(booking_id):
    status = request.form.get('status')
    if status not in ['pending', 'accepted', 'declined']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    row = db.get_booking_by_id(booking_id)
    if not row:
        abort(404)
    db.update_booking_status(booking_id, status)
    booking = format_booking(db.get_booking_by_id(booking_id))
    notify_status_change(booking)
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)