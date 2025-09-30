from flask import Flask, render_template, request, redirect, url_for, flash
import qrcode
import base64
from io import BytesIO
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  
ATTENDANCE_FILE = 'attendance.csv'

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# QR code generation
@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')

        if not student_id or not student_name:
            flash('Please enter both Student ID and Name.')
            return redirect(url_for('generate_qr'))

        data = f"{student_id},{student_name}"
        qr_img = qrcode.make(data)
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return render_template('generate_qr.html', qr_code=img_str, student_id=student_id, student_name=student_name)

    return render_template('generate_qr.html')

# Attendance mark karne ka page
@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')

        if not student_id or not student_name:
            flash('Please enter both Student ID and Name.')
            return redirect(url_for('mark_attendance'))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # CSV file me attendance record add karo
        file_exists = os.path.isfile(r'D:\codes\Python\new\qr_attendance\attendance.csv')
        with open(r'D:\codes\Python\new\qr_attendance\attendance.csv', 'a', newline='') as csvfile:
            fieldnames = ['Student_ID', 'Name', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({'Student_ID': student_id, 'Name': student_name, 'Timestamp': now})

        flash(f'Attendance marked for {student_name} at {now}')
        return redirect(url_for('mark_attendance'))

    return render_template('mark_attendance.html')

# Attendance report page
@app.route('/report')
def report():
    if not os.path.isfile(r'D:\codes\Python\new\qr_attendance\attendance.csv'):
        flash('No attendance records found.')
        return redirect(url_for('index'))

    with open(r'D:\codes\Python\new\qr_attendance\attendance.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        records = list(reader)

    unique_students = {record['Student_ID'] for record in records if 'Student_ID' in record}
    total_present = len(unique_students)

    total_students = 20
    total_absent = total_students - total_present

    return render_template('report.html', total_present=total_present, total_absent=total_absent, records=records)

if __name__ == '__main__':
    app.run(debug=True, port=8080)