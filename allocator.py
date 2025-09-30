import random
from collections import defaultdict
from database import get_all_students, get_all_rooms, insert_allocation, clear_allocations, log_activity

def allocate_rollwise():
    clear_allocations()
    
    students = get_all_students()
    rooms = get_all_rooms()
    
    if not students or not rooms:
        return False, "No students or rooms available"
    
    students_sorted = sorted(students, key=lambda x: x['roll_no'])
    
    room_seats = []
    for room in rooms:
        for row in range(1, room['rows'] + 1):
            for col in range(1, room['columns'] + 1):
                if len(room_seats) < sum(r['capacity'] for r in rooms):
                    room_seats.append({
                        'room_no': room['room_no'],
                        'row': row,
                        'col': col,
                        'seat_number': f"{room['room_no']}-R{row}C{col}"
                    })
    
    allocated = 0
    for i, student in enumerate(students_sorted):
        if i < len(room_seats):
            seat = room_seats[i]
            insert_allocation(
                student['roll_no'],
                seat['room_no'],
                seat['row'],
                seat['col'],
                seat['seat_number'],
                'rollwise'
            )
            allocated += 1
    
    log_activity('allocation', f'Roll-wise allocation completed: {allocated} students allocated')
    return True, f"Successfully allocated {allocated} students"

def allocate_random():
    clear_allocations()
    
    students = get_all_students()
    rooms = get_all_rooms()
    
    if not students or not rooms:
        return False, "No students or rooms available"
    
    students_list = list(students)
    random.shuffle(students_list)
    
    room_seats = []
    for room in rooms:
        for row in range(1, room['rows'] + 1):
            for col in range(1, room['columns'] + 1):
                if len(room_seats) < sum(r['capacity'] for r in rooms):
                    room_seats.append({
                        'room_no': room['room_no'],
                        'row': row,
                        'col': col,
                        'seat_number': f"{room['room_no']}-R{row}C{col}"
                    })
    
    allocated = 0
    for i, student in enumerate(students_list):
        if i < len(room_seats):
            seat = room_seats[i]
            insert_allocation(
                student['roll_no'],
                seat['room_no'],
                seat['row'],
                seat['col'],
                seat['seat_number'],
                'random'
            )
            allocated += 1
    
    log_activity('allocation', f'Random allocation completed: {allocated} students allocated')
    return True, f"Successfully allocated {allocated} students"

def allocate_anti_cheating():
    clear_allocations()
    
    students = get_all_students()
    rooms = get_all_rooms()
    
    if not students or not rooms:
        return False, "No students or rooms available"
    
    subject_groups = defaultdict(list)
    for student in students:
        subject_groups[student['subject_code']].append(student)
    
    for subject in subject_groups:
        random.shuffle(subject_groups[subject])
    
    room_seats = []
    for room in rooms:
        for row in range(1, room['rows'] + 1):
            for col in range(1, room['columns'] + 1):
                if len(room_seats) < sum(r['capacity'] for r in rooms):
                    room_seats.append({
                        'room_no': room['room_no'],
                        'row': row,
                        'col': col,
                        'seat_number': f"{room['room_no']}-R{row}C{col}",
                        'assigned': False,
                        'subject': None
                    })
    
    allocated = 0
    subject_list = list(subject_groups.keys())
    subject_indices = {subject: 0 for subject in subject_list}
    
    for seat_idx, seat in enumerate(room_seats):
        best_subject = None
        best_distance = -1
        
        for subject in subject_list:
            if subject_indices[subject] >= len(subject_groups[subject]):
                continue
            
            min_distance = float('inf')
            for check_idx in range(max(0, seat_idx - 5), seat_idx):
                if room_seats[check_idx]['assigned'] and room_seats[check_idx]['subject'] == subject:
                    distance = seat_idx - check_idx
                    min_distance = min(min_distance, distance)
            
            if min_distance == float('inf'):
                min_distance = 999
            
            if min_distance > best_distance:
                best_distance = min_distance
                best_subject = subject
        
        if best_subject and best_distance >= 2:
            student = subject_groups[best_subject][subject_indices[best_subject]]
            subject_indices[best_subject] += 1
            
            seat['assigned'] = True
            seat['subject'] = best_subject
            
            insert_allocation(
                student['roll_no'],
                seat['room_no'],
                seat['row'],
                seat['col'],
                seat['seat_number'],
                'anti-cheating'
            )
            allocated += 1
    
    for subject in subject_list:
        while subject_indices[subject] < len(subject_groups[subject]):
            for seat in room_seats:
                if not seat['assigned']:
                    student = subject_groups[subject][subject_indices[subject]]
                    subject_indices[subject] += 1
                    
                    seat['assigned'] = True
                    seat['subject'] = subject
                    
                    insert_allocation(
                        student['roll_no'],
                        seat['room_no'],
                        seat['row'],
                        seat['col'],
                        seat['seat_number'],
                        'anti-cheating'
                    )
                    allocated += 1
                    break
            else:
                break
    
    log_activity('allocation', f'Anti-cheating allocation completed: {allocated} students allocated')
    return True, f"Successfully allocated {allocated} students with anti-cheating algorithm"
