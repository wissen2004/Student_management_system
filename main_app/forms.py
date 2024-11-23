from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)

        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True, label="Электронная почта")
    gender = forms.ChoiceField(choices=[('M', 'Мужчина'), ('F', 'Женщина')], label="Пол")
    first_name = forms.CharField(required=True, label="Имя")
    last_name = forms.CharField(required=True, label="Фамилия")
    address = forms.CharField(widget=forms.Textarea, label="Адрес")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    profile_pic = forms.ImageField(label="Фото профиля")

    widget = {
        'password': forms.PasswordInput(),
    }

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Заполните, только если хотите изменить пароль"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "Данный электронный адрес уже зарегистрирован")
        else:
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("Данный электронный адрес уже зарегистрирован")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'password', 'profile_pic', 'address']


class StudentForm(CustomUserForm):
    course = forms.ChoiceField(label="Курс")
    session = forms.ChoiceField(label="Сессия")
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['course'].choices = [(course.id, course.name) for course in Course.objects.all()]
        self.fields['session'].choices = [(session.id, f'{session.start_year} - {session.end_year}') for session in
                                              Session.objects.all()]

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    course = forms.ChoiceField(label="Курс")
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['course'].choices = [(course.id, course.name) for course in Course.objects.all()]

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['course' ]


class CourseForm(FormSettings):
    name = forms.CharField(label="Название курса")
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Course


class SubjectForm(FormSettings):
    name = forms.CharField(label="Название предмета")
    course = forms.ChoiceField(label="Курс")
    staff = forms.ChoiceField(label="Преподователь")
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['course'].choices = [(course.id, course.name) for course in Course.objects.all()]
        self.fields['staff'].choices = [(staff.id, f'{staff.admin.last_name} {staff.admin.first_name}') for staff in Staff.objects.all()]

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


class SessionForm(FormSettings):
    start_year = forms.DateField(widget=DateInput(attrs={'type': 'date', 'placeholder': 'Год начала'}),
                                 label="Год начала")
    end_year = forms.DateField(widget=DateInput(attrs={'type': 'date', 'placeholder': 'Год окончания'}),
                               label="Год окончания")
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)


    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    date = forms.DateField(widget=DateInput(attrs={'type': 'date', 'placeholder': 'Год начала'}),
                                 label="Дата")
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Сообщение'}), label="Сообщение")
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }



class LeaveReportStudentForm(FormSettings):
    date = forms.DateField(widget=DateInput(attrs={'type': 'date', 'placeholder': 'Год начала'}),
                                 label="Дата")
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Сообщение'}), label="Сообщение")
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Сессия", queryset=session_list, required=True)
    subject = forms.ModelChoiceField(label="Предмет", queryset=Subject.objects.all(), required=True)
    student = forms.ModelChoiceField(label="Студент", queryset=Student.objects.all(), required=True)
    test = forms.IntegerField(label="Тест", required=True)
    exam = forms.IntegerField(label="Экзамен", required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']
