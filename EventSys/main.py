from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# DATABASE CONNECTION

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="arisha",  
        database="eventdb"
    )

# PYDANTIC MODELS

class Event(BaseModel):
    title: str
    date: str
    venue: str
    capacity: int

class Registration(BaseModel):
    sapid: str
    studentname: str
    department: str
    email: str
    eventid: int
    status: str = "Registered"

class AttendanceUpdate(BaseModel):
    attendance_status: str

class StudentUser(BaseModel):
    fullname: str
    sapid: str
    email: str
    password: str

class LoginUser(BaseModel):
    sapid: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str


# PAGE ROUTES

@app.get("/student-page", response_class=HTMLResponse)
def student_home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")

@app.get("/events-page", response_class=HTMLResponse)
def events_page(request: Request):
    return templates.TemplateResponse(request, "events.html")

@app.get("/admin", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "admin_login.html")

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse(request, "admin_dashboard.html")

@app.get("/admin/events", response_class=HTMLResponse)
def admin_events(request: Request):
    return templates.TemplateResponse(request, "admin_events.html")

@app.get("/admin/participants", response_class=HTMLResponse)
def admin_participants(request: Request):
    return templates.TemplateResponse(request, "admin_participants.html")

@app.get("/admin/attendance", response_class=HTMLResponse)
def admin_attendance_page(request: Request):
    return templates.TemplateResponse(request, "admin_attendance.html")


# STUDENT AUTH ROUTES

@app.post("/student/signup")
def student_signup(user: StudentUser):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE sapid=%s", (user.sapid,))
        existing = cursor.fetchone()
        if existing:
            con.close()
            return {"error": "SAP ID already registered"}
        cursor.execute(
            "INSERT INTO students (fullname, sapid, email, password) VALUES (%s, %s, %s, %s)",
            (user.fullname, user.sapid, user.email, user.password)
        )
        con.commit()
        con.close()
        return {"message": "Signup successful"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/student/login")
def student_login(user: LoginUser):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM students WHERE sapid=%s AND password=%s",
            (user.sapid, user.password)
        )
        result = cursor.fetchone()
        con.close()
        if result:
            return {"message": "Login successful", "student": result}
        else:
            return {"message": "Invalid SAP ID or password"}
    except Exception as e:
        return {"error": str(e)}


# ADMIN AUTH ROUTE

@app.post("/admin/login")
def admin_login(user: AdminLogin):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM admins WHERE username=%s AND password=%s",
            (user.username, user.password)
        )
        result = cursor.fetchone()
        con.close()
        if result:
            return {"message": "Login successful", "admin": result}
        else:
            return {"message": "Invalid admin credentials"}
    except Exception as e:
        return {"error": str(e)}


# EVENT ROUTES (Admin manages)

@app.get("/events")
def get_all_events():
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, 
                   COUNT(r.sapid) AS registered_count
            FROM events e
            LEFT JOIN registrations r ON e.eventid = r.eventid
            GROUP BY e.eventid
            ORDER BY e.date ASC
        """)
        records = cursor.fetchall()
        con.close()
        return records
    except Exception as e:
        return {"error": str(e)}

@app.get("/events/{eventid}")
def get_single_event(eventid: int):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE eventid=%s", (eventid,))
        record = cursor.fetchone()
        con.close()
        return record
    except Exception as e:
        return {"error": str(e)}

@app.post("/events")
def add_event(event: Event):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO events (title, date, venue, capacity) VALUES (%s, %s, %s, %s)",
            (event.title, event.date, event.venue, event.capacity)
        )
        con.commit()
        con.close()
        return {"message": "Event added successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.put("/events/{eventid}")
def update_event(eventid: int, event: Event):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute(
            "UPDATE events SET title=%s, date=%s, venue=%s, capacity=%s WHERE eventid=%s",
            (event.title, event.date, event.venue, event.capacity, eventid)
        )
        con.commit()
        con.close()
        return {"message": "Event updated successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/events/{eventid}")
def delete_event(eventid: int):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM events WHERE eventid=%s", (eventid,))
        con.commit()
        con.close()
        return {"message": "Event deleted successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/events")
def delete_all_events():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM events")
        con.commit()
        con.close()
        return {"message": "All events deleted"}
    except Exception as e:
        return {"error": str(e)}

# REGISTRATION ROUTES (Students register)

@app.get("/registrations/event/{eventid}")
def get_registrations_by_event(eventid: int):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM registrations WHERE eventid=%s ORDER BY studentname ASC",
            (eventid,)
        )
        records = cursor.fetchall()
        con.close()
        return records
    except Exception as e:
        return {"error": str(e)}

@app.get("/registrations/student/{sapid}")
def get_registrations_by_student(sapid: str):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, e.title, e.date, e.venue
            FROM registrations r
            JOIN events e ON r.eventid = e.eventid
            WHERE r.sapid=%s
        """, (sapid,))
        records = cursor.fetchall()
        con.close()
        return records
    except Exception as e:
        return {"error": str(e)}

@app.post("/registrations")
def add_registration(reg: Registration):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        # Check duplicate
        cursor.execute(
            "SELECT * FROM registrations WHERE sapid=%s AND eventid=%s",
            (reg.sapid, reg.eventid)
        )
        if cursor.fetchone():
            con.close()
            return {"error": "You are already registered for this event"}
        cursor.execute(
            "INSERT INTO registrations (sapid, studentname, department, email, eventid, status) VALUES (%s,%s,%s,%s,%s,%s)",
            (reg.sapid, reg.studentname, reg.department, reg.email, reg.eventid, reg.status)
        )
        # Also insert into attendance with "Not Marked" status
        cursor.execute(
            "INSERT INTO attendance (sapid, studentname, eventid, attendance_status) VALUES (%s,%s,%s,%s)",
            (reg.sapid, reg.studentname, reg.eventid, "Not Marked")
        )
        con.commit()
        con.close()
        return {"message": "Registration successful"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/registrations/{sapid}/{eventid}")
def delete_registration(sapid: str, eventid: int):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM registrations WHERE sapid=%s AND eventid=%s", (sapid, eventid))
        cursor.execute("DELETE FROM attendance WHERE sapid=%s AND eventid=%s", (sapid, eventid))
        con.commit()
        con.close()
        return {"message": "Registration removed"}
    except Exception as e:
        return {"error": str(e)}


# ATTENDANCE ROUTES (Admin marks attendance)

@app.get("/attendance/event/{eventid}")
def get_attendance_by_event(eventid: int):
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM attendance WHERE eventid=%s ORDER BY studentname ASC",
            (eventid,)
        )
        records = cursor.fetchall()
        con.close()
        return records
    except Exception as e:
        return {"error": str(e)}

@app.put("/attendance/{attendanceid}")
def update_attendance(attendanceid: int, att: AttendanceUpdate):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute(
            "UPDATE attendance SET attendance_status=%s WHERE attendanceid=%s",
            (att.attendance_status, attendanceid)
        )
        con.commit()
        con.close()
        return {"message": "Attendance updated"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/attendance/{attendanceid}")
def delete_attendance(attendanceid: int):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM attendance WHERE attendanceid=%s", (attendanceid,))
        con.commit()
        con.close()
        return {"message": "Record deleted"}
    except Exception as e:
        return {"error": str(e)}
