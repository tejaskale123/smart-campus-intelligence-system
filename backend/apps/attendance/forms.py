from django import forms


class AttendanceForm(forms.Form):
    student_id = forms.CharField()
    attendance_date = forms.DateField()
    status = forms.ChoiceField(
        choices=(
            ("Present", "Present"),
            ("Absent", "Absent"),
        )
    )
