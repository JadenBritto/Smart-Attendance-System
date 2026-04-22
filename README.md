# Smart Attendance System

A Django-based intelligent attendance management system using face recognition technology to automatically detect and record student attendance via webcam.

## Features

- **Face Recognition**: Real-time facial recognition using webcam to automatically mark attendance
- **Student Management**: Register students with facial data and profile information
- **Attendance Sessions**: Create and manage attendance sessions with custom date, time, and subject
- **User Roles**: Three-tier role system (Admin, Class Teacher, Teacher) with role-based access control
- **Attendance Reports**: View attendance records, generate statistics, and export data (CSV/Excel)
- **Dashboard**: Overview of attendance statistics with visual progress indicators
- **Responsive UI**: Modern dark sidebar interface with Tailwind CSS
- **Manual Override**: Ability to manually toggle student attendance status if needed

## Technology Stack

- **Backend**: Django 6.0.3
- **Python**: 3.12
- **Face Recognition**: face_recognition, dlib, OpenCV
- **Database**: SQLite (development)
- **Frontend**: HTML/CSS with Tailwind CSS (CDN)
- **Data Export**: Pandas, openpyxl

## System Requirements

- Windows 10 or later (or Linux/Mac with appropriate system libraries)
- Python 3.12
- Pip package manager
- Webcam for face recognition

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Smart Attendance System"
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first installation may take a few minutes as it builds face recognition dependencies.

### 4. Initialize Database

```bash
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Running the Server

Start the development server:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Login

1. Go to the login page
2. Enter your admin credentials
3. You'll be directed to the dashboard

## Usage Guide

### For Administrators

1. **Manage Users**: Create and manage system users (Admin, Class Teachers, Teachers)
   - Navigate to Users → User Management
   - Add new users and assign roles

2. **Manage Departments**: Create academic departments
   - Navigate to Classes → Departments
   - Add department name and code

3. **Manage Classes**: Create class sections under departments
   - Navigate to Classes → Classes
   - Specify class name, department, year, and section

### For Class Teachers

1. **Register Students**: Add students to your assigned class
   - Navigate to Students → Student Management
   - Add student details and capture face data (via webcam or file upload)
   - Face encoding will be automatically generated

2. **Take Attendance**: Record attendance for a class session
   - Navigate to Attendance → Take Attendance
   - Select your class (auto-populated if assigned)
   - Set date, time, and subject
   - Webcam feed will appear - students' faces will be automatically recognized
   - Manually toggle any attendance status if needed
   - Close the session when complete

3. **View Reports**: Check attendance statistics
   - Navigate to Attendance → Reports
   - Filter by date, class, or subject
   - Export data as CSV or Excel

### For Teachers

- View attendance reports (read-only access)
- Cannot create or modify attendance sessions

## Project Structure

```
Smart Attendance System/
├── smart_attendance/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  # User authentication & management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── classes/                   # Department & class management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── students/                  # Student registration & face data
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── attendance/                # Attendance sessions & records
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── recognition/               # Face recognition utilities
│   ├── utils.py
│   ├── detector.py
│   ├── encoder.py
│   └── matcher.py
├── templates/                 # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── classes/
│   ├── students/
│   └── attendance/
├── static/
│   └── js/                    # JavaScript utilities
│       ├── webcam.js
│       └── attendance.js
├── media/                     # Student photos & data storage
├── manage.py
├── requirements.txt
└── README.md
```

## Key Models

### User
- Custom user model extending Django's AbstractUser
- Fields: username, email, password, first_name, last_name, role, assigned_class
- Roles: admin, class_teacher, teacher

### Student
- Fields: roll_number, first_name, last_name, class_section, photo
- Has associated FaceEncoding for recognition

### FaceEncoding
- Stores 128-dimensional face vectors as JSON
- Links to student record
- Enables real-time face matching

### AttendanceSession
- Fields: class_section, date, subject, start_time, end_time
- Created by class teachers
- Is_active flag indicates ongoing sessions

### AttendanceRecord
- Fields: session, student, status (present/absent), recognized_at, confidence
- Tracks individual student attendance

## API Endpoints

### Face Detection
- **POST** `/api/detect-face/` - Detect face in uploaded/captured image
- Returns: Face encoding (128-dimensional vector)

### Face Recognition
- **POST** `/api/recognize-faces/` - Match captured face against student database
- Returns: Matched student or no match

## Troubleshooting

### Camera Not Working
- Ensure webcam permissions are granted to the browser
- Try a different browser (Chrome/Edge recommended)
- Verify webcam is not in use by another application

### Face Recognition Not Working
- Ensure face is clearly visible and well-lit
- Check that student face encoding exists (captured during registration)
- Adjust camera angle if face is partially visible

### Database Errors
- Delete `db.sqlite3` and run migrations again:
  ```bash
  rm db.sqlite3
  python manage.py migrate
  ```

### Dependency Installation Issues
- Ensure Python 3.12 is being used: `python --version`
- Upgrade pip: `python -m pip install --upgrade pip`
- If dlib fails, it uses pre-built binaries (dlib-bin) - verify it's installed

## Future Enhancements

- Multiple camera support
- Email attendance notifications
- Parent portal for attendance viewing
- Advanced analytics and predictive analysis
- Integration with existing school management systems
- Mobile app for teacher access
- Biometric authentication for system login

## License

This project is developed for educational purposes.

## Support

For issues or questions, please check the troubleshooting section or review the Django logs:

```bash
# Enable debug logging (development only)
tail -f logs/debug.log
```
