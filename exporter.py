import os
import io
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import pandas as pd
from database import get_all_allocations, get_allocation_by_roll, get_student_by_roll
from datetime import datetime

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer

def generate_admit_card_pdf(roll_no, output_path):
    allocation = get_allocation_by_roll(roll_no)
    
    if not allocation:
        return False
    
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 1 * inch, "EXAM ADMIT CARD")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 1.3 * inch, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    y_position = height - 2 * inch
    c.setFont("Helvetica-Bold", 12)
    
    details = [
        ("Roll Number:", allocation['roll_no']),
        ("Name:", allocation['name']),
        ("Course/Program:", allocation['course']),
        ("Semester:", allocation['semester']),
        ("Subject Code:", allocation['subject_code']),
        ("", ""),
        ("Exam Room:", f"{allocation['room_no']} - {allocation['building']}"),
        ("Seat Number:", allocation['seat_number']),
        ("Row:", str(allocation['row_num'])),
        ("Column:", str(allocation['col_num']))
    ]
    
    for label, value in details:
        if label:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1.5 * inch, y_position, label)
            c.setFont("Helvetica", 12)
            c.drawString(3.5 * inch, y_position, str(value))
        y_position -= 0.4 * inch
    
    qr_data = f"Roll: {allocation['roll_no']} | Room: {allocation['room_no']} | Seat: {allocation['seat_number']}"
    qr_buffer = generate_qr_code(qr_data)
    qr_image = ImageReader(qr_buffer)
    
    qr_x = width / 2 - 1 * inch
    qr_y = 2 * inch
    # c.drawImage(qr_buffer, qr_x, qr_y, width=2 * inch, height=2 * inch, mask='auto')
    
    # c.setFont("Helvetica-Oblique", 10)
    c.drawImage(qr_image, qr_x, qr_y, width=2 * inch, height=2 * inch, mask='auto') 

    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 1.5 * inch, "Scan QR code for verification")
    
    # ... existing code ...
    
    # 🟢 FIX: Border ko pura draw karein
    c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch, stroke=1, fill=0)
    
    # 🟢 FIX: Instruction ki starting Y-position ko upar rakhein (e.g., 1.5 inch)
    y_inst_start = 1.5 * inch 

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1 * inch, y_inst_start, "Important Instructions:")
    
    c.setFont("Helvetica", 9)
    instructions = [
        "1. Bring this admit card to the examination hall",
        "2. Report 30 minutes before exam start time",
        "3. Carry a valid ID proof",
        "4. Mobile phones and electronic devices are not allowed"
    ]
    
    # 🟢 FIX: Instructions ko Border ke andar adjust karein
    y_inst = y_inst_start - 0.25 * inch 
    for instruction in instructions:
        c.drawString(1 * inch, y_inst, instruction)
        y_inst -= 0.15 * inch # Line spacing

    c.save()
    return True
def generate_all_admit_cards():
    allocations = get_all_allocations()
    
    if not allocations:
        return False, "No allocations found"
    
    output_dir = 'exports/admit_cards'
    os.makedirs(output_dir, exist_ok=True)
    
    for allocation in allocations:
        filename = f"{allocation['roll_no']}_admit_card.pdf"
        filepath = os.path.join(output_dir, filename)
        generate_admit_card_pdf(allocation['roll_no'], filepath)
    
    return True, f"Generated {len(allocations)} admit cards in {output_dir}"

def export_seating_plan_excel():
    allocations = get_all_allocations()
    
    if not allocations:
        return None
    
    data = []
    for allocation in allocations:
        data.append({
            'Roll No': allocation['roll_no'],
            'Name': allocation['name'],
            'Course': allocation['course'],
            'Semester': allocation['semester'],
            'Subject Code': allocation['subject_code'],
            'Email': allocation['email'],
            'Room No': allocation['room_no'],
            'Building': allocation['building'],
            'Seat Number': allocation['seat_number'],
            'Row': allocation['row_num'],
            'Column': allocation['col_num'],
            'Allocation Method': allocation['allocation_method']
        })
    
    df = pd.DataFrame(data)
    
    output_path = 'exports/seating_plan.xlsx'
    os.makedirs('exports', exist_ok=True)
    
    df.to_excel(output_path, index=False, sheet_name='Seating Plan')
    
    return output_path

def export_room_wise_excel(room_no):
    from database import get_allocations_by_room
    
    allocations = get_allocations_by_room(room_no)
    
    if not allocations:
        return None
    
    data = []
    for allocation in allocations:
        data.append({
            'Seat Number': allocation['seat_number'],
            'Row': allocation['row_num'],
            'Column': allocation['col_num'],
            'Roll No': allocation['roll_no'],
            'Name': allocation['name'],
            'Course': allocation['course'],
            'Subject Code': allocation['subject_code'],
            'Email': allocation['email']
        })
    
    df = pd.DataFrame(data)
    
    output_path = f'exports/room_{room_no}_list.xlsx'
    os.makedirs('exports', exist_ok=True)
    
    df.to_excel(output_path, index=False, sheet_name=f'Room {room_no}')
    
    return output_path
