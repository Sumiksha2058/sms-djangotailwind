# Student Management System (SMS)

This is a Student Management System built with **Django** (Python) and styled using **Tailwind CSS**.

The application implements the data model derived from the provided project structure, covering core entities and features like:
*   Users with Role-Based Access Control (Admin, Teacher, Student, Parent)
*   Courses and Subjects
*   Teachers, Students, and Parents
*   Attendance, Assignments, and Results

## Setup and Installation

### Prerequisites
*   Python 3.x
*   Node.js and npm (for Tailwind CSS build)

### 1. Clone the Repository (or extract the project files)
Assuming you have the project files in your current directory.

### 2. Install Python Dependencies
```bash
pip install django django-environ
```

### 3. Install Node Dependencies (for Tailwind CSS)
```bash
npm install -D tailwindcss postcss autoprefixer
npm install -D tailwindcss-cli # To ensure the CLI is available
```

### 4. Database Migrations
Apply the initial database migrations:
```bash
python3 manage.py makemigrations core
python3 manage.py migrate
```

### 5. Create Superuser
Create an administrative user to access the Django Admin panel:
```bash
python3 manage.py createsuperuser
# Follow the prompts to set username, email, and password
```
**Note:** A superuser with username `admin` and password `password` was created during the setup process.

### 6. Build Tailwind CSS
Generate the final CSS file from the utility classes used in the templates:
```bash
./node_modules/.bin/tailwindcss-cli -i ./static/css/input.css -o ./static/css/output.css
```

### 7. Run the Development Server
```bash
python3 manage.py runserver
```
The application will be available at `http://127.0.0.1:8000/`.

## Application Access

*   **Homepage:** `/`
*   **Django Admin:** `/admin/` (Use the superuser credentials)
*   **Courses:** `/courses/`
*   **Students:** `/students/`
*   **Teachers:** `/teachers/`
*   **Subjects:** `/subjects/`
*   **Attendance:** `/attendance/`
*   **Assignments:** `/assignments/`
*   **Results:** `/results/`

## Data Model Overview

The system uses the following core models:

| Model | Description | Key Fields |
| :--- | :--- | :--- |
| `UserProfile` | Extends Django's `User` for roles (admin, teacher, student, parent). | `user`, `role`, `phone` |
| `Course` | Represents a class or section. | `name`, `code`, `semester`, `class_teacher` |
| `Subject` | Represents a course content. | `name`, `code`, `credits` |
| `Teacher` | Teacher-specific information. | `user_profile`, `employee_id`, `department` |
| `Student` | Student-specific information. | `user_profile`, `roll_number`, `course`, `parent` |
| `Attendance` | Tracks daily attendance. | `student`, `subject`, `attendance_date`, `status` |
| `Assignment` | Details of an assignment. | `subject`, `teacher`, `due_date`, `total_marks` |
| `Result` | Stores student grades/marks. | `student`, `subject`, `exam`, `marks_obtained`, `grade` |

## Next Steps (Potential Enhancements)

1.  **Authentication:** Implement proper login/logout views for non-admin users.
2.  **Parent/Timetable CRUD:** Implement CRUD for the remaining `Parent` and `Timetable` models.
3.  **UI/UX:** Further refine the Tailwind CSS styling and add a dedicated dashboard view.
4.  **Permissions:** Implement view-level permissions based on the `UserProfile` role.
