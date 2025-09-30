import sqlite3
import pandas as pd
from datetime import datetime

def get_connection():
    conn = sqlite3.connect('exam_seating.db')
    conn.row_factory = sqlite3.Row
    return conn

def clear_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students')
    conn.commit()
    conn.close()

def clear_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rooms')
    conn.commit()
    conn.close()

def clear_allocations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM seating_allocations')
    conn.commit()
    conn.close()

def insert_students(df):
    conn = get_connection()
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO students (roll_no, name, course, semester, email, subject_code)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(row['Roll No']), str(row['Name']), str(row['Course/Program']), 
                  str(row['Semester']), str(row['Email']), str(row['Subject Code'])))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

def insert_rooms(df):
    conn = get_connection()
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO rooms (room_no, building, rows, columns, capacity)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(row['Room No']), str(row['Building']), int(row['Rows']), 
                  int(row['Columns']), int(row['Capacity'])))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    students = cursor.execute('SELECT * FROM students ORDER BY roll_no').fetchall()
    conn.close()
    return students

def get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    rooms = cursor.execute('SELECT * FROM rooms ORDER BY room_no').fetchall()
    conn.close()
    return rooms

def get_student_by_roll(roll_no):
    conn = get_connection()
    cursor = conn.cursor()
    student = cursor.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,)).fetchone()
    conn.close()
    return student

def get_allocation_by_roll(roll_no):
    conn = get_connection()
    cursor = conn.cursor()
    allocation = cursor.execute('''
        SELECT sa.*, s.name, s.course, s.semester, s.subject_code, r.building
        FROM seating_allocations sa
        JOIN students s ON sa.roll_no = s.roll_no
        JOIN rooms r ON sa.room_no = r.room_no
        WHERE sa.roll_no = ?
    ''', (roll_no,)).fetchone()
    conn.close()
    return allocation

def get_allocations_by_room(room_no):
    conn = get_connection()
    cursor = conn.cursor()
    allocations = cursor.execute('''
        SELECT sa.*, s.name, s.course, s.semester, s.subject_code, s.email
        FROM seating_allocations sa
        JOIN students s ON sa.roll_no = s.roll_no
        WHERE sa.room_no = ?
        ORDER BY sa.row_num, sa.col_num
    ''', (room_no,)).fetchall()
    conn.close()
    return allocations

def get_all_allocations():
    conn = get_connection()
    cursor = conn.cursor()
    allocations = cursor.execute('''
        SELECT sa.*, s.name, s.course, s.semester, s.subject_code, s.email, r.building
        FROM seating_allocations sa
        JOIN students s ON sa.roll_no = s.roll_no
        JOIN rooms r ON sa.room_no = r.room_no
        ORDER BY sa.room_no, sa.row_num, sa.col_num
    ''').fetchall()
    conn.close()
    return allocations

def insert_allocation(roll_no, room_no, row_num, col_num, seat_number, method):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO seating_allocations (roll_no, room_no, row_num, col_num, seat_number, allocation_method)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (roll_no, room_no, row_num, col_num, seat_number, method))
    conn.commit()
    conn.close()

def log_activity(activity_type, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_log (activity_type, description)
        VALUES (?, ?)
    ''', (activity_type, description))
    conn.commit()
    conn.close()

def validate_students_file(df):
    required_columns = ['Roll No', 'Name', 'Course/Program', 'Semester', 'Email', 'Subject Code']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing columns: {', '.join(missing_columns)}"
    
    if df['Roll No'].duplicated().any():
        duplicates = df[df['Roll No'].duplicated()]['Roll No'].tolist()
        return False, f"Duplicate roll numbers found: {', '.join(map(str, duplicates[:5]))}"
    
    return True, "Valid"

def validate_rooms_file(df):
    required_columns = ['Room No', 'Building', 'Rows', 'Columns', 'Capacity']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing columns: {', '.join(missing_columns)}"
    
    if df['Room No'].duplicated().any():
        duplicates = df[df['Room No'].duplicated()]['Room No'].tolist()
        return False, f"Duplicate room numbers found: {', '.join(map(str, duplicates[:5]))}"
    
    return True, "Valid"

def check_capacity():
    conn = get_connection()
    cursor = conn.cursor()
    
    total_students = cursor.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_capacity = cursor.execute('SELECT SUM(capacity) FROM rooms').fetchone()[0]
    
    conn.close()
    
    if total_capacity is None:
        total_capacity = 0
    
    return total_students, total_capacity, total_students <= total_capacity
