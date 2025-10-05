from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session, flash 
from datetime import datetime, timedelta
import os
import sqlite3
# Import io for correct file stream handling in pandas
import io 
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXPORT_FOLDER'] = 'exports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)


 

@app.template_filter('datetimeformat')
def format_datetime(value, format_str='%b %d, %Y %I:%M %p'):
    if value is None:
        return ""

    if isinstance(value, str):
        try:
            # Check for microseconds
            if '.' in value:
                dt_utc = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
            else:
                dt_utc = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value 
    else:
        dt_utc = value

    # IST = UTC + 5 hours 30 minutes
    dt_ist = dt_utc + timedelta(hours=5, minutes=30)

    return dt_ist.strftime(format_str)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db():
    conn = sqlite3.connect('exam_seating.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, 
        is_admin BOOLEAN DEFAULT 0
    )
''')
    
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Default password: adminpass
        from werkzeug.security import generate_password_hash
        default_admin_password = generate_password_hash('adminpass') 
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin) 
            VALUES (?, ?, ?)
        ''', ('admin', default_admin_password, 1))
        print("Default admin user 'admin' created with password 'adminpass'")
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            semester TEXT NOT NULL,
            email TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_no TEXT UNIQUE NOT NULL,
            building TEXT NOT NULL,
            rows INTEGER NOT NULL,
            columns INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seating_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            room_no TEXT NOT NULL,
            row_num INTEGER NOT NULL,
            col_num INTEGER NOT NULL,
            seat_number TEXT NOT NULL,
            allocation_method TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (roll_no) REFERENCES students (roll_no),
            FOREIGN KEY (room_no) REFERENCES rooms (room_no)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

#routes
# ... (init_db function yahan end hota hai)
# ...

@app.route('/') 
def index():
    # Agar user logged in hai, toh admin dashboard par bheje
    #if 'logged_in' in session and session['logged_in']:
    is_user_logged_in = 'logged_in' in session and session.get('logged_in')
        # Ab hum 'admin' endpoint ka upyog kar rahe hain (neeche dekhein)
        #return redirect(url_for('admin')) 
        
    # Agar logged in nahi hai, toh login page par bheje
    #return redirect(url_for('login'))
    return render_template('index.html', logged_in=is_user_logged_in)
# ...

# app.py (around Line 229)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 🟢 FIX 1: 'username' ko form ke 'email' field se lein
        username = request.form.get('email')
        
        # NOTE: Agar aap HTML form mein 'name' aur 'phone' field ka name attribute use kar rahe hain
        name = request.form.get('name') 
        phone = request.form.get('phone') 
        
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password or not confirm_password:
            # Data wapas bhejne ki koshish
            flash("All fields are required.", 'danger')
            return render_template('registration.html', 
                                   email=username, 
                                   name=name, 
                                   phone=phone)
        
        if password != confirm_password:
            flash("Passwords do not match.", 'danger')
            return render_template('registration.html', 
                                   email=username, 
                                   name=name, 
                                   phone=phone)
            
        # 1. Password ko Hash karein
        hashed_password = generate_password_hash(password)
        
        # 2. User ko database mein insert karein
        from database import insert_user
        
        # 💡 Yahaan missing code tha
        if insert_user(username, hashed_password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login')) 
        else:
            # 💡 Yahaan missing code tha: Agar insertion fail hota hai (e.g., username exists), toh yeh return ho
            flash("Username already exists.", 'danger')
            return render_template('registration.html', email=username, name=name, phone=phone)

    # 💡 Yahaan missing code tha: GET request ke liye
    return render_template('registration.html')
#S
@app.route('/admin') # 🔴 FIX: Added the missing decorator for the admin dashboard
def admin():
    """Displays the admin dashboard with stats and recent activity."""
    # Security check 
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
#E
 


    conn = get_db()
    cursor = conn.cursor()
    
    student_count = cursor.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    room_count = cursor.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    allocation_count = cursor.execute('SELECT COUNT(*) FROM seating_allocations').fetchone()[0]
    
    recent_activities = cursor.execute('''
        SELECT * FROM activity_log 
        ORDER BY timestamp DESC LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin.html', 
                            student_count=student_count,
                            room_count=room_count,
                            allocation_count=allocation_count,
                            recent_activities=recent_activities)

@app.route('/student')
def student_portal():
    return render_template('student.html')

@app.route('/invigilator')
def invigilator_panel():
    conn = get_db()
    cursor = conn.cursor()
    
    rooms = cursor.execute('SELECT * FROM rooms ORDER BY room_no').fetchall()
    conn.close()
    
    return render_template('invigilator.html', rooms=rooms)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        from database import get_user_by_username
        user = get_user_by_username(username)
        
        # 1. User check karein aur Hashed Password verify karein
        if user and check_password_hash(user['password_hash'], password):
            # Login Successful
            session['logged_in'] = True
            session['username'] = user['username']
            session['is_admin'] = user['is_admin'] # Optional: check for admin status
            
            return redirect(url_for('admin'))
        else:
            # Login Failed
            return render_template('login.html', error="Invalid username or password.")
    
    return render_template('login.html')

#just
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))
#end


@app.route('/api/upload_students', methods=['POST'])
def upload_students():
    # Assuming 'database' module exists and has these functions
    from database import validate_students_file, insert_students, log_activity, clear_students
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file format. Use CSV or Excel'}), 400
    
    try:
        if file.filename.endswith('.csv'):
            # 🔴 FIX: Using io.TextIOWrapper for correct CSV reading from FileStorage stream
            df = pd.read_csv(io.TextIOWrapper(file.stream, encoding='utf-8'))
        else:
            # Excel files are read correctly using the stream directly
            df = pd.read_excel(file.stream)
            df.columns = df.columns.str.strip()
        
        valid, message = validate_students_file(df)
        
        if not valid:
            return jsonify({'success': False, 'message': message}), 400
        
        clear_students()
        insert_students(df)
        log_activity('upload', f'Uploaded {len(df)} students')
        
        return jsonify({'success': True, 'message': f'Successfully uploaded {len(df)} students'})
    
    except Exception as e:
        # Detailed error message for debugging
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/api/upload_rooms', methods=['POST'])
def upload_rooms():
    # Assuming 'database' module exists and has these functions
    from database import validate_rooms_file, insert_rooms, log_activity, clear_rooms
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file format. Use CSV or Excel'}), 400
    
    try:
        if file.filename.endswith('.csv'):
            # 🔴 FIX: Using io.TextIOWrapper for correct CSV reading from FileStorage stream
            df = pd.read_csv(io.TextIOWrapper(file.stream, encoding='utf-8'))
        else:
            # Excel files are read correctly using the stream directly
            df = pd.read_excel(file.stream)
            df.columns = df.columns.str.strip()
        
        valid, message = validate_rooms_file(df)
        
        if not valid:
            return jsonify({'success': False, 'message': message}), 400
        
        clear_rooms()
        insert_rooms(df)
        log_activity('upload', f'Uploaded {len(df)} rooms')
        
        return jsonify({'success': True, 'message': f'Successfully uploaded {len(df)} rooms'})
    
    except Exception as e:
        # Detailed error message for debugging
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/api/allocate', methods=['POST'])
def allocate_seats():
    from database import check_capacity
    from allocator import allocate_rollwise, allocate_random, allocate_anti_cheating
    
    data = request.get_json()
    method = data.get('method', 'anti-cheating')
    
    student_count, capacity, sufficient = check_capacity()
    
    if not sufficient:
        return jsonify({
            'success': False, 
            'message': f'Insufficient capacity: {student_count} students but only {capacity} seats'
        }), 400
    
    try:
        if method == 'rollwise':
            success, message = allocate_rollwise()
        elif method == 'random':
            success, message = allocate_random()
        else:
            success, message = allocate_anti_cheating()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during allocation: {str(e)}'}), 500

@app.route('/api/generate_admit_cards', methods=['POST'])
def generate_cards():
    from exporter import generate_all_admit_cards
    
    try:
        success, message = generate_all_admit_cards()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating admit cards: {str(e)}'}), 500

@app.route('/api/export_excel', methods=['GET'])
def export_excel():
    from exporter import export_seating_plan_excel
    
    try:
        filepath = export_seating_plan_excel()
        
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name='seating_plan.xlsx')
        else:
            return jsonify({'success': False, 'message': 'No allocations found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error exporting Excel: {str(e)}'}), 500

@app.route('/api/student/<roll_no>', methods=['GET'])
def get_student_seat(roll_no):
    from database import get_allocation_by_roll
    
    allocation = get_allocation_by_roll(roll_no)
    
    if allocation:
        return jsonify({
            'success': True,
            'data': {
                'roll_no': allocation['roll_no'],
                'name': allocation['name'],
                'course': allocation['course'],
                'semester': allocation['semester'],
                'subject_code': allocation['subject_code'],
                'room_no': allocation['room_no'],
                'building': allocation['building'],
                'seat_number': allocation['seat_number'],
                'row': allocation['row_num'],
                'column': allocation['col_num']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Seat allocation not found'}), 404

@app.route('/api/download_admit_card/<roll_no>', methods=['GET'])
def download_admit_card(roll_no):
    from exporter import generate_admit_card_pdf
    
    filepath = f'exports/admit_cards/{roll_no}_admit_card.pdf'
    
    if not os.path.exists(filepath):
        os.makedirs('exports/admit_cards', exist_ok=True)
        success = generate_admit_card_pdf(roll_no, filepath)
        
        if not success:
            return jsonify({'success': False, 'message': 'Could not generate admit card'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=f'{roll_no}_admit_card.pdf')

@app.route('/api/room/<room_no>/allocations', methods=['GET'])
def get_room_allocations(room_no):
    from database import get_allocations_by_room, get_all_rooms
    
    rooms = get_all_rooms()
    room = next((r for r in rooms if r['room_no'] == room_no), None)
    
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404
    
    allocations = get_allocations_by_room(room_no)
    
    seat_map = {}
    for allocation in allocations:
        key = f"{allocation['row_num']}-{allocation['col_num']}"
        seat_map[key] = {
            'roll_no': allocation['roll_no'],
            'name': allocation['name'],
            'course': allocation['course'],
            'subject_code': allocation['subject_code'],
            'seat_number': allocation['seat_number']
        }
    
    return jsonify({
        'success': True,
        'room': {
            'room_no': room['room_no'],
            'building': room['building'],
            'rows': room['rows'],
            'columns': room['columns'],
            'capacity': room['capacity']
        },
        'allocations': seat_map
    })

@app.route('/api/room/<room_no>/export', methods=['GET'])
def export_room_list(room_no):
    from exporter import export_room_wise_excel
    
    try:
        filepath = export_room_wise_excel(room_no)
        
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=f'room_{room_no}_list.xlsx')
        else:
            return jsonify({'success': False, 'message': 'No allocations found for this room'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error exporting room list: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    student_count = cursor.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    room_count = cursor.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    allocation_count = cursor.execute('SELECT COUNT(*) FROM seating_allocations').fetchone()[0]
    total_capacity = cursor.execute('SELECT SUM(capacity) FROM rooms').fetchone()[0] or 0
    
    room_utilization = []
    rooms = cursor.execute('SELECT * FROM rooms').fetchall()
    for room in rooms:
        allocated = cursor.execute('''
            SELECT COUNT(*) FROM seating_allocations WHERE room_no = ?
        ''', (room['room_no'],)).fetchone()[0]
        
        room_utilization.append({
            'room_no': room['room_no'],
            'capacity': room['capacity'],
            'allocated': allocated,
            'percentage': round((allocated / room['capacity'] * 100), 1) if room['capacity'] > 0 else 0
        })
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'students': student_count,
            'rooms': room_count,
            'allocations': allocation_count,
            'total_capacity': total_capacity,
            'room_utilization': room_utilization
        }
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)