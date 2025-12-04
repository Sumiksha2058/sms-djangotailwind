import pandas as pd
from django.db.models import Avg
from core.models import Student, Result, Attendance

def export_training_data():
    data = []

    students = Student.objects.all()

    for s in students:
        attendance_count = Attendance.objects.filter(student=s, status="Present").count()
        total_attendance = Attendance.objects.filter(student=s).count()

        attendance_percentage = (attendance_count / total_attendance * 100) if total_attendance > 0 else 0

        avg_marks = Result.objects.filter(student=s).aggregate(Avg("marks_obtained"))["marks_obtained__avg"] or 0

        label = 1 if avg_marks >= 40 else 0  # pass if >= 40

        data.append({
            "attendance": attendance_percentage,
            "avg_marks": avg_marks,
            "pass_fail": label,
        })

    df = pd.DataFrame(data)
    df.to_csv("ml/pass_fail_training_data.csv", index=False)
    print("Training data exported successfully.")
