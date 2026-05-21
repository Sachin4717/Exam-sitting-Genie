# Exam Sitting Genie

Exam Sitting Genie is a robust, scalable, and automated **exam seating allocation system** designed to streamline the process of assigning students to examination seats. It eliminates manual errors, reduces administrative workload, and ensures optimal utilization of examination halls. The solution is well-suited for academic institutions seeking efficiency, accuracy, and reliability in examination management.

---

## Overview

Managing exam seating manually becomes increasingly complex as student numbers grow. Exam Sitting Genie provides a systematic and automated approach to seat allocation, ensuring fairness, transparency, and consistency across examination centers.

---

## Key Features

- Automated seat allocation based on predefined rules  
- Exam-wise seating plan generation  
- Support for multiple examination halls with varying capacities  
- Secure student record management  
- Conflict-free and duplicate-free seat assignments  
- Scalable architecture suitable for large institutions  
- Significant reduction in manual effort and time  

---

## Technology Stack

- **Frontend:** HTML5, CSS3, Bootstrap  
- **Backend:** Python (Django Framework)  
- **Database:** SQLite (development), PostgreSQL (production-ready)  
- **Version Control:** Git and GitHub  

---

## Project Structure

```
Exam-Sitting-Genie/
│
├── manage.py
├── requirements.txt
├── README.md
├── apps/
│   ├── students/
│   ├── halls/
│   └── allocation/
├── templates/
├── static/
└── db.sqlite3
```

---

## Installation and Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/exam-sitting-genie.git
cd exam-sitting-genie
```

### Step 2: Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Run the Development Server
```bash
python manage.py runserver
```

Access the application at:  
http://127.0.0.1:8000/

---

## Application Workflow

1. Configure examination halls and seating capacity  
2. Register student and examination details  
3. Execute the seat allocation process  
4. Generate and review seating arrangements  

---

## Intended Users

- Colleges and Universities  
- Schools and Educational Institutions  
- Competitive and Entrance Examination Centers  

---

## Project Highlights

- Designed using real-world academic use cases  
- Emphasizes automation, accuracy, and scalability  
- Suitable for hackathons, academic projects, and professional portfolios  

---

## Future Enhancements

- Export seating plans to PDF and Excel formats  
- Administrative dashboard with analytics and reports  
- Role-based authentication and access control  
- Cloud deployment and scalability support  

---

## Author

**Sachin Kumar**  
GitHub: https://github.com/Sachin4717  

---

## License

This project is licensed under the MIT License.  
You are free to use, modify, and distribute this software with proper attribution.

---

If you find this project useful, consider starring the repository on GitHub.
