from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.dispatch import receiver
import datetime
import uuid
# Create your models here.
class SessionYearModel(models.Model):
    id=models.AutoField(primary_key=True)
    session_start_year=models.DateField()
    session_end_year=models.DateField()
    object=models.Manager()

class CustomUser(AbstractUser):
    user_type_data=((1,"HOD"),(2,"Staff"),(3,"Student"),(4,"Parent"),(5,"Account"))
    user_type=models.CharField(default=1,choices=user_type_data,max_length=10)

class AdminHOD(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    profile_pic=models.FileField(default="")
    objects=models.Manager()

class Staffs(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    profile_pic=models.FileField(default="")
    fcm_token=models.TextField(default="")
    objects=models.Manager()
    
class Accounts(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    profile_pic=models.FileField(default="")
    fcm_token=models.TextField(default="")
    objects=models.Manager()

class Courses(models.Model):
    id=models.AutoField(primary_key=True)
    course_name=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()


class Subjects(models.Model):
    id=models.AutoField(primary_key=True)
    subject_name=models.CharField(max_length=255)
    course_id=models.ForeignKey(Courses,on_delete=models.CASCADE,default=1)
    staff_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Students(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    gender=models.CharField(max_length=255)
    profile_pic=models.FileField()
    address=models.TextField()
    course_id=models.ForeignKey(Courses,on_delete=models.DO_NOTHING)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects = models.Manager()


class Attendance(models.Model):
    id=models.AutoField(primary_key=True)
    subject_id=models.ForeignKey(Subjects,on_delete=models.DO_NOTHING)
    attendance_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students,on_delete=models.DO_NOTHING)
    attendance_id=models.ForeignKey(Attendance,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class LeaveReportStudent(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students,on_delete=models.CASCADE)
    leave_start_date=models.CharField(max_length=255)
    leave_end_date=models.CharField(max_length=255, default="")
    leave_message=models.TextField()
    leave_status=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_start_date=models.CharField(max_length=255)
    leave_end_date=models.CharField(max_length=255, default="")
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class LeaveReportAccount(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    leave_start_date=models.CharField(max_length=255)
    leave_end_date=models.CharField(max_length=255, default="")
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class FeedBackAccounts(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class NotificationAccounts(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class StudentResult(models.Model):
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField()
    subject_assignment_marks = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)



class OnlineClassRoom(models.Model):
    id=models.AutoField(primary_key=True)
    room_name=models.CharField(max_length=255)
    room_pwd=models.CharField(max_length=255)
    subject=models.ForeignKey(Subjects,on_delete=models.CASCADE)
    session_years=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    started_by=models.ForeignKey(Staffs,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_on=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class News(models.Model):
    id=models.AutoField(primary_key=True)
    ntext = models.TextField()
    ntitle = models.TextField(max_length=4000)
    ndate=models.DateTimeField(auto_now_add=True, blank=True)
    pic=models.FileField(default="", blank=True, null=True)
    objects=models.Manager()
    
class TNews(models.Model):
    id=models.AutoField(primary_key=True)
    ntext = models.TextField()
    ntitle = models.TextField(max_length=4000)
    ndate=models.DateTimeField(auto_now_add=True, blank=True)
    pic=models.FileField(default="", blank=True, null=True)
    objects=models.Manager()
    
class ANews(models.Model):
    id=models.AutoField(primary_key=True)
    ntext = models.TextField()
    ntitle = models.TextField(max_length=4000)
    ndate=models.DateTimeField(auto_now_add=True, blank=True)
    pic=models.FileField(default="", blank=True, null=True)
    objects=models.Manager()
    
class SComment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    News = models.ForeignKey(News, on_delete=models.CASCADE, related_name="comments")
    staff_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,default=1)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    count = models.IntegerField(default="1")
    reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    objects=models.Manager()

class TComment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    TNews = models.ForeignKey(TNews, on_delete=models.CASCADE, related_name="comments")
    staff_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,default=1)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    count = models.IntegerField(default="1")
    reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    objects=models.Manager()

class AComment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ANews = models.ForeignKey(ANews, on_delete=models.CASCADE, related_name="comments")
    staff_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,default=1)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    count = models.IntegerField(default="1")
    reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    objects=models.Manager()
    
class Parents(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    profile_pic=models.FileField(default="")
    fcm_token=models.TextField(default="")
    objects=models.Manager()

class FeedBackParents(models.Model):
    id = models.AutoField(primary_key=True)
    parent_id = models.ForeignKey(Parents, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class NotificationParents(models.Model):
    id = models.AutoField(primary_key=True)
    parent_id = models.ForeignKey(Parents, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class PNews(models.Model):
    id=models.AutoField(primary_key=True)
    ntext = models.TextField()
    ntitle = models.TextField(max_length=4000)
    ndate=models.DateTimeField(auto_now_add=True, blank=True)
    pic=models.FileField(default="", blank=True, null=True)
    objects=models.Manager()
    
class PComment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    PNews = models.ForeignKey(PNews, on_delete=models.CASCADE, related_name="comments")
    staff_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,default=1)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    count = models.IntegerField(default="1")
    reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    objects=models.Manager()
    
class Finance(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    FEES_TYPE_CHOICES = [
        ('lunch', 'Lunch'),
        ('transport', 'Transport'),
        ('tuition', 'Tuition'),
    ]
    fees_type = models.CharField(max_length=10, choices=FEES_TYPE_CHOICES)
    fee_due = models.DecimalField(max_digits=8, decimal_places=2)
    fees_paid = models.DecimalField(max_digits=8, decimal_places=2)
    fee_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.fee_balance = self.fee_due - self.fees_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student} - {self.fees_type}'    
    
class Invoice(models.Model):
    id=models.AutoField(primary_key=True)
    student=models.CharField(max_length=255)
    student_email = models.EmailField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True, default=2348)
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    message = models.TextField(default= "Payment before the due date is appreciated.")
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    status = models.BooleanField(default=False)
    paid = models.DecimalField(max_digits=9, decimal_places=2)
    balance=models.DecimalField(max_digits=9, decimal_places=2)
    def __str__(self):
        return str(self.student)
    
    def get_status(self):
        return self.status

    # def save(self, *args, **kwargs):
        # if not self.id:             
        #     self.due_date = datetime.datetime.now()+ datetime.timedelta(days=15)
        # return super(Invoice, self).save(*args, **kwargs)

               
class LineItem(models.Model):
    id=models.AutoField(primary_key=True)
    student=models.ForeignKey(Invoice,on_delete=models.CASCADE)
    service = models.TextField()
    description = models.TextField()
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=9, decimal_places=2)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return str(self.student)

class DefaultSettings(models.Model):
    lunch_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_and_lunch_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_and_transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_and_lunch_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_lunch_transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return "Default Settings"

        
class FinancialRecord(models.Model):
    id=models.AutoField(primary_key=True)
    created_at=models.DateTimeField(auto_now_add=True)
    FEE_TYPE_CHOICES = [
        ('lunch', 'Lunch'),
        ('transport', 'Transport'),
        ('tuition', 'Tuition'),
        ('transport and lunch', 'Transport and Lunch'),
        ('tuition and transport', 'Tuition and Transport'),
        ('tuition and lunch', 'Tuition and Lunch'),
        ('tuition, lunch and transport', 'Tuition, Lunch and Transport'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    date = models.DateField()
    fee_type = models.CharField(max_length=255, choices=FEE_TYPE_CHOICES)
    fee_balance = models.DecimalField(max_digits=9, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2)
    new_balance = models.DecimalField(max_digits=9, decimal_places=2)
    
       

@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        if instance.user_type==1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type==2:
            Staffs.objects.create(admin=instance,address="")
        if instance.user_type==3:
            Students.objects.create(admin=instance,course_id=Courses.objects.get(id=1),session_year_id=SessionYearModel.object.get(id=1),address="",profile_pic="",gender="")
        if instance.user_type==4:
            Parents.objects.create(admin=instance,profile_pic="",student_id=Students.objects.get(id=3))
        if instance.user_type==5:
            Accounts.objects.create(admin=instance,address="")            

@receiver(post_save,sender=CustomUser)
def save_user_profile(sender,instance,**kwargs):
    if instance.user_type==1:
        instance.adminhod.save()
    if instance.user_type==2:
        instance.staffs.save()
    if instance.user_type==3:
        instance.students.save()
    if instance.user_type==4:
        instance.parents.save()
    if instance.user_type==5:
        instance.accounts.save()
