import json

import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.db.models import Sum
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
import pdfkit
import datetime
import io
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.template import Context
from django.db import transaction
    


from school_management_app.forms import AddStudentForm, EditStudentForm, InvoiceForm,LineItemFormset
from school_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, \
    FeedBackStudent, FeedBackStaffs, FeedBackAccounts, LeaveReportStudent, LeaveReportStaff, LeaveReportAccount, Attendance, AttendanceReport, \
    NotificationStudent, NotificationStaffs, NotificationAccounts, News, TNews, TComment, SComment, ANews, AComment, AdminHOD, Parents, PNews ,PComment, FeedBackParents, NotificationParents, Invoice, LineItem, Finance, Accounts, FinancialRecord, DefaultSettings


def admin_home(request):
    student_count1=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    subject_count=Subjects.objects.all().count()
    course_count=Courses.objects.all().count()
    parent_count=Parents.objects.all().count()
    account_count=Accounts.objects.all().count()
    finance_count=FinancialRecord.objects.all().count()

    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)

    course_all=Courses.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects=Subjects.objects.filter(course_id=course.id).count()
        students=Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course_id.id)
        student_count=Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staffs.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)



    return render(request,"hod_template/home_content.html",{"student_count":student_count1,"staff_count":staff_count,"parent_count":parent_count,"account_count":account_count,"subject_count":subject_count,"course_count":course_count,  "finance_count":finance_count, "course_name_list":course_name_list,"subject_count_list":subject_count_list,"student_count_list_in_course":student_count_list_in_course,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"staff_name_list":staff_name_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student,"admin":admin})

def add_staff(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_staff_template.html",{"admin":admin})

def add_staff_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        default_profile_pic="/media/default.png"
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.staffs.address=address
            if profile_pic_url!=None:
                user.staffs.profile_pic=profile_pic_url
            else:
                user.staffs.profile_pic=default_profile_pic
            user.save()
            messages.success(request,"Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request,"Failed to Add Staff ")
            return HttpResponseRedirect(reverse("add_staff"))
            
def add_account(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_account_template.html",{"admin":admin})

def add_account_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        default_profile_pic="/media/default.png"
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=5)
            user.accounts.address=address
            if profile_pic_url!=None:
                user.accounts.profile_pic=profile_pic_url
            else:
                user.accounts.profile_pic=default_profile_pic
            user.save()
            messages.success(request,"Successfully Added Accountant")
            return HttpResponseRedirect(reverse("add_account"))
        except:
            messages.error(request,"Failed to Add Accountant ")
            return HttpResponseRedirect(reverse("add_account"))

def add_course(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_course_template.html",{"admin":admin})

def add_course_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        course=request.POST.get("course")
        try:
            course_model=Courses(course_name=course)
            course_model.save()
            messages.success(request,"Successfully Added Grade")
            return HttpResponseRedirect(reverse("add_course"))
        except Exception as e:
            print(e)
            messages.error(request,"Failed to Add Grade")
            return HttpResponseRedirect(reverse("add_course"))

def add_student(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    form=AddStudentForm()
    return render(request,"hod_template/add_student_template.html",{"form":form,"admin":admin})

def add_student_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            sex=form.cleaned_data["sex"]

            default_profile_pic="/media/default.png"
            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None
            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.students.address=address

                course_obj=Courses.objects.get(id=course_id)
                user.students.course_id=course_obj

                session_year=SessionYearModel.object.get(id=session_year_id)
                user.students.session_year_id=session_year
                
                user.students.gender=sex
                if profile_pic_url!=None:
                    user.students.profile_pic=profile_pic_url
                else:
                    user.students.profile_pic=default_profile_pic
                user.save()
                messages.success(request,"Successfully added student")
                return HttpResponseRedirect(reverse("add_student"))
            except:
                messages.error(request,"Failed to add student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form=AddStudentForm(request.POST)
            return render(request, "hod_template/add_student_template.html", {"form": form})


def add_subject(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/add_subject_template.html",{"staffs":staffs,"courses":courses,"admin":admin})

def add_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        course_id=request.POST.get("course")
        course=Courses.objects.get(id=course_id)
        staff_id=request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)

        try:
            subject=Subjects(subject_name=subject_name,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,"Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))


def manage_staff(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    staffs=Staffs.objects.all()
    return render(request,"hod_template/manage_staff_template.html",{"staffs":staffs,"admin":admin})
    
def manage_account(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    accounts=Accounts.objects.all()
    return render(request,"hod_template/manage_account_template.html",{"accounts":accounts,"admin":admin})

def manage_student(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    students=Students.objects.all()
    return render(request,"hod_template/manage_student_template.html",{"students":students,"admin":admin})

def manage_course(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    courses=Courses.objects.all()
    return render(request,"hod_template/manage_course_template.html",{"courses":courses,"admin":admin})

def manage_subject(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    subjects=Subjects.objects.all()
    return render(request,"hod_template/manage_subject_template.html",{"subjects":subjects,"admin":admin})

def edit_staff(request,staff_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    staff=Staffs.objects.get(admin=staff_id)
    return render(request,"hod_template/edit_staff_template.html",{"staff":staff,"id":staff_id,"admin":admin})

def edit_staff_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id=request.POST.get("staff_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            if profile_pic_url!=None:
                staff_model.profile_pic=profile_pic_url
            staff_model.save()
            messages.success(request,"Successfully Edited Staff")
            return HttpResponseRedirect(reverse("manage_staff"))
        except:
            messages.error(request,"Failed to Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

def delete_staff(request,staff_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=staff_id)
            user.delete()
            messages.success(request,"Successfully Deleted Staff")
            return HttpResponseRedirect(reverse("manage_staff"))
        except:
            messages.error(request,"Failed to Delete Staff")
            return HttpResponseRedirect(reverse("manage_staff"))
            
def edit_account(request,account_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    account=Accounts.objects.get(admin=account_id)
    return render(request,"hod_template/edit_account_template.html",{"account":account,"id":account_id,"admin":admin})

def edit_account_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        account_id=request.POST.get("account_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.get(id=account_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            account_model=Accounts.objects.get(admin=account_id)
            account_model.address=address
            if profile_pic_url!=None:
                account_model.profile_pic=profile_pic_url
            account_model.save()
            messages.success(request,"Successfully Edited Accountant")
            return HttpResponseRedirect(reverse("manage_account"))
        except:
            messages.error(request,"Failed to Edit Accountant")
            return HttpResponseRedirect(reverse("edit_account",kwargs={"account_id":account_id}))

def delete_account(request,account_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=account_id)
            user.delete()
            messages.success(request,"Successfully Deleted Accountant")
            return HttpResponseRedirect(reverse("manage_account"))
        except:
            messages.error(request,"Failed to Delete Accountant")
            return HttpResponseRedirect(reverse("manage_account"))


def edit_student(request,student_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    request.session['student_id']=student_id
    student=Students.objects.get(admin=student_id)
    form=EditStudentForm()
    form.fields['email'].initial=student.admin.email
    form.fields['first_name'].initial=student.admin.first_name
    form.fields['last_name'].initial=student.admin.last_name
    form.fields['username'].initial=student.admin.username
    form.fields['address'].initial=student.address
    form.fields['course'].initial=student.course_id.id
    form.fields['sex'].initial=student.gender
    form.fields['session_year_id'].initial=student.session_year_id.id
    return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username,"admin":admin})

def edit_student_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id=request.session.get("student_id")
        if student_id==None:
            return HttpResponseRedirect(reverse("manage_student"))

        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None
            try:
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()

                student=Students.objects.get(admin=student_id)
                student.address=address
                session_year=SessionYearModel.object.get(id=session_year_id)
                student.session_year_id=session_year
                student.gender=sex
                course=Courses.objects.get(id=course_id)
                student.course_id=course
                if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Successfully Edited Student")
                return HttpResponseRedirect(reverse("manage_student"))
            except:
                messages.error(request,"Failed to Edit Student")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            student=Students.objects.get(admin=student_id)
            return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

def delete_student(request,student_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=student_id)
            user.delete()

            messages.success(request,"Successfully Deleted Student")
            return HttpResponseRedirect(reverse("manage_student"))
        except:
            messages.error(request,"Failed to Delete Student")
            return HttpResponseRedirect(reverse("manage_student"))

def edit_subject(request,subject_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    subject=Subjects.objects.get(id=subject_id)
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/edit_subject_template.html",{"subject":subject,"admin":admin,"staffs":staffs,"courses":courses,"id":subject_id})

def edit_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")
        subject_name=request.POST.get("subject_name")
        staff_id=request.POST.get("staff")
        course_id=request.POST.get("course")

        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.subject_name=subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Courses.objects.get(id=course_id)
            subject.course_id=course
            subject.save()

            messages.success(request,"Successfully Edited Subject")
            return HttpResponseRedirect(reverse("manage_subject"))
        except:
            messages.error(request,"Failed to Edit Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))

def delete_subject(request,subject_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.delete()
            messages.success(request,"Successfully Deleted Subject")
            return HttpResponseRedirect(reverse("manage_subject"))
        except:
            messages.error(request,"Failed to Delete Subject")
            return HttpResponseRedirect(reverse("manage_subject"))


def edit_course(request,course_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    course=Courses.objects.get(id=course_id)
    return render(request,"hod_template/edit_course_template.html",{"course":course,"admin":admin,"id":course_id})

def edit_course_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id=request.POST.get("course_id")
        course_name=request.POST.get("course")
        try:
            course=Courses.objects.get(id=course_id)
            print(Courses.course_name)
            course.course_name=course_name
            course.save()
            messages.success(request,"Successfully Edited Grade")
            return HttpResponseRedirect(reverse("manage_course"))
        except:
            messages.error(request,"Failed to Edit Grade")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))

def delete_course(request,course_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            course=Courses.objects.get(id=course_id)
            course.delete()
            messages.success(request,"Successfully Deleted Grade")
            return HttpResponseRedirect(reverse("manage_course"))
        except:
            messages.error(request,"Failed to Delete Grade")
            return HttpResponseRedirect(reverse("manage_course"))


def manage_session(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    sessions=SessionYearModel.object.all()
    return render(request,"hod_template/manage_session.html",{"sessions":sessions,"admin":admin})

def add_session(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/manage_session_template.html",{"admin":admin})

def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Term Dates")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Term Dates")
            return HttpResponseRedirect(reverse("manage_session"))

def edit_session(request, session_id):
    user = CustomUser.objects.get(id=request.user.id)
    admin = AdminHOD.objects.get(admin=user)
    session = SessionYearModel.object.get(id=session_id)
    return render(request, "hod_template/edit_session_template.html", {"session": session, "admin": admin})

def edit_session_save(request, session_id):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("edit_session", args=[session_id]))
    else:
        session_start_year = request.POST.get("session_start")
        session_end_year = request.POST.get("session_end")

        try:
            sessionyear = SessionYearModel.object.get(id=session_id)
            sessionyear.session_start_year = session_start_year
            sessionyear.session_end_year = session_end_year
            sessionyear.save()

            messages.success(request, "Successfully Edited Term Dates")
            return HttpResponseRedirect(reverse("edit_session", args=[session_id]))
        except SessionYearModel.DoesNotExist:
            messages.error(request, "Session does not exist")
            return HttpResponseRedirect(reverse("edit_session", args=[session_id]))

def delete_session(request,session_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            session=SessionYearModel.object.get(id=session_id)
            session.delete()
            messages.success(request,"Successfully Deleted Term Dates")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request,"Failed to Delete Term Dates")
            return HttpResponseRedirect(reverse("manage_session"))

def manage_news(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=News.objects.all()
    return render(request,"hod_template/manage_news.html",{"news":news,"admin":admin})

def add_news(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_news_template.html",{"admin":admin})

def add_news_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=News(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Added News")
            return HttpResponseRedirect(reverse("manage_news"))
        except:
            messages.error(request,"Failed to Add News")
            return HttpResponseRedirect(reverse("manage_news"))

def edit_news(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(News.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Failed to Edit News")
        return HttpResponseRedirect(reverse("manage_news"))
    news=News.objects.get(id=news_id)
    return render(request,"hod_template/edit_news_template.html",{"news":news,"admin":admin})

def edit_news_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=News.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Edited News")
            return HttpResponseRedirect(reverse("manage_news"))
        except:
            messages.error(request,"Failed to Edit News")
            return HttpResponseRedirect(reverse("manage_news"))

def delete_news(request,news_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=News.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Successfully Deleted News ")
            return HttpResponseRedirect(reverse("manage_news"))
        except:
            messages.error(request,"Failed to Delete News")
            return HttpResponseRedirect(reverse("manage_news"))

def view_news(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news = News.objects.get(id=news_id)
    comment=SComment.objects.filter(News=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_news.html",{"news":news,"comment":comment,"admin":admin,"comment_count":comments_count,"staff":staff})
    

def manage_tnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news = TNews.objects.all()
    return render(request,"hod_template/manage_tnews.html",{"news":news,"admin":admin})

def add_tnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_tnews_template.html",{"admin":admin})

def add_tnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=TNews(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Added News")
            return HttpResponseRedirect(reverse("manage_tnews"))
        except:
            messages.error(request,"Failed to Add News")
            return HttpResponseRedirect(reverse("manage_tnews"))

def edit_tnews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(TNews.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Failed to Edit News")
        return HttpResponseRedirect(reverse("manage_tnews"))
    news=TNews.objects.get(id=news_id)
    return render(request,"hod_template/edit_tnews_template.html",{"news":news,"admin":admin})

def edit_tnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=TNews.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Edited News")
            return HttpResponseRedirect(reverse("manage_tnews"))
        except:
            messages.error(request,"Failed to Edit News")
            return HttpResponseRedirect(reverse("manage_tnews"))

def delete_tnews(request,news_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=TNews.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Successfully Deleted News")
            return HttpResponseRedirect(reverse("manage_tnews"))
        except:
            messages.error(request,"Failed to Delete News")
            return HttpResponseRedirect(reverse("manage_tnews"))

def view_tnews(request, news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=TNews.objects.get(id=news_id)
    comment=TComment.objects.filter(TNews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_tnews.html",{"news":news,"admin":admin,"comment":comment,"comment_count":comments_count,"staff":staff})

# POST TEACHER COMMENT
def view_staff_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_tnews"))
    else:
        TNews = request.POST.get("TNews_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = TComment.objects.get(id=reply_id)
        try:
            Tcomment=TComment(TNews_id=TNews, staff_id=staff, body=body, count=a, reply=comment_qs)
            Tcomment.save()
            messages.success(request, "Successfully Posted Comment!")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Failed to Post Comment")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))
# EDIT TEACHER COMMENT
def view_staff_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_tnews"))
    else:
        comment_id = request.POST.get("comment_id")
        TNews = request.POST.get("TNews_id")
        body = request.POST.get("body")
        try:
            comment = TComment.objects.get(id=comment_id)
            comment.TNews_id=TNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Successfuy Edited Comment!")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Failed to Edit Comment ")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))

def delete_tcomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=TComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Successfully deleted Comment")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":news_id}))
            
def manage_anews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=ANews.objects.all()
    return render(request,"hod_template/manage_anews.html",{"news":news,"admin":admin})

def add_anews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_anews_template.html",{"admin":admin})

def add_anews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=ANews(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Added News")
            return HttpResponseRedirect(reverse("manage_anews"))
        except:
            messages.error(request,"Failed to Add News")
            return HttpResponseRedirect(reverse("manage_anews"))

def edit_anews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(ANews.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Failed to Edit News")
        return HttpResponseRedirect(reverse("manage_anews"))
    news=ANews.objects.get(id=news_id)
    return render(request,"hod_template/edit_anews_template.html",{"news":news,"admin":admin})

def edit_anews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=ANews.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Edited News")
            return HttpResponseRedirect(reverse("manage_anews"))
        except:
            messages.error(request,"Failed to Edit News")
            return HttpResponseRedirect(reverse("manage_anews"))

# DELETE ACCOUNTANT COMMENT
def delete_acomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=AComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Successfully deleted Comment")
            return HttpResponseRedirect(reverse("view_anews",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_anews",kwargs={"news_id":news_id}))
        
def view_account_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_anews"))
    else:
        comment_id = request.POST.get("comment_id")
        TNews = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = AComment.objects.get(id=comment_id)
            comment.ANews_id=TNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Successfully Edited Comment ")
            return HttpResponseRedirect(reverse("view_anews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Failed to Edit Comment ")
            return HttpResponseRedirect(reverse("view_anews",kwargs={"news_id":TNews}))


def delete_anews(request,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=ANews.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Successfully Deleted News ")
            return HttpResponseRedirect(reverse("manage_anews"))
        except:
            messages.error(request,"Failed to Delete News")
            return HttpResponseRedirect(reverse("manage_anews"))
            

def view_anews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news = ANews.objects.get(id=news_id)
    comment=AComment.objects.filter(ANews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_anews.html",{"news":news,"comment":comment,"admin":admin,"comment_count":comments_count,"staff":staff})
    
# POST TEACHER COMMENT
def view_account_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_anews"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = AComment.objects.get(id=reply_id)
        try:
            Acomment=AComment(ANews_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            Acomment.save()
            messages.success(request, "Successfully Posted Comment!")
            return HttpResponseRedirect(reverse("view_anews",kwargs={"news_id":News}))
        except:
            messages.error(request, "Failed to Post Comment")
            return HttpResponseRedirect(reverse("view_anews",kwargs={"news_id":News}))

# POST STUDENT COMMENT
def view_student_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_news"))
    else:
        SNews = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = SComment.objects.get(id=reply_id)
        try:
            Scomment=SComment(News_id=SNews, staff_id=staff, body=body, count=a, reply=comment_qs)
            Scomment.save()
            messages.success(request, "Successfully Posted Comment")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))
        except:
            messages.error(request, "Failed to Post Comment")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))

# EDIT STUDENT COMMENT
def view_student_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_news"))
    else:
        comment_id = request.POST.get("comment_id")
        SNews = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = SComment.objects.get(id=comment_id)
            comment.News_id=SNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Successfully Edited Comment ")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))
        except:
            messages.error(request, "Failed to Edit Comment ")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))
            


# DELETE STUDENT COMMENT
def delete_scomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=SComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Successfuly Deleted Comment")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":news_id}))

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def staff_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackStaffs.objects.all()
    return render(request,"hod_template/staff_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})

def student_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackStudent.objects.all()
    return render(request,"hod_template/student_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})

def parent_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackParents.objects.all()
    return render(request,"hod_template/parent_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})
    
def account_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackAccounts.objects.all()
    return render(request,"hod_template/account_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def parent_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackParents.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")
        
@csrf_exempt
def account_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackAccounts.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def staff_leave_view(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    leaves=LeaveReportStaff.objects.all()
    return render(request,"hod_template/staff_leave_view.html",{"leaves":leaves,"admin":admin})

def student_leave_view(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    leaves=LeaveReportStudent.objects.all()
    return render(request,"hod_template/student_leave_view.html",{"leaves":leaves,"admin":admin})
    
def account_leave_view(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    leaves=LeaveReportAccount.objects.all()
    return render(request,"hod_template/account_leave_view.html",{"leaves":leaves,"admin":admin})

def student_approve_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

def student_disapprove_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def staff_approve_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def staff_disapprove_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))
    
def account_approve_leave(request,leave_id):
    leave=LeaveReportAccount.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("account_leave_view"))

def account_disapprove_leave(request,leave_id):
    leave=LeaveReportAccount.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("account_leave_view"))

def admin_view_attendance(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.object.all()
    return render(request,"hod_template/admin_view_attendance.html",{"subjects":subjects,"admin":admin,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/admin_profile.html",{"user":user,"admin":admin})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            admin=AdminHOD.objects.get(admin=customuser)
            if profile_pic_url!=None:
                admin.profile_pic=profile_pic_url
            admin.save()
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Added Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Add Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_student(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    students=Students.objects.all()
    notification=NotificationStudent.objects.all()
    return render(request,"hod_template/student_notification.html",{"students":students,"admin":admin,"notification":notification})

def delete_student_notifications(request,id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=NotificationStudent.objects.get(id=id)
            mv.delete()
            messages.success(request,"Successfully Deleted Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_student"))
        except:
            messages.error(request,"Failed to Delete Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_student"))

def admin_send_notification_staff(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    staffs=Staffs.objects.all()
    notification=NotificationStaffs.objects.all()
    return render(request,"hod_template/staff_notification.html",{"staffs":staffs,"admin":admin,"notification":notification})

def delete_staff_notifications(request,id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=NotificationStaffs.objects.get(id=id)
            mv.delete()
            messages.success(request,"Successfully Deleted Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_staff"))
        except:
            messages.error(request,"Failed to Delete Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_staff"))
            
def admin_send_notification_account(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    accounts=Accounts.objects.all()
    notification=NotificationAccounts.objects.all()
    return render(request,"hod_template/account_notification.html",{"accounts":accounts,"admin":admin,"notification":notification})

def delete_account_notifications(request,id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=NotificationAccounts.objects.get(id=id)
            mv.delete()
            messages.success(request,"Successfully Deleted Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_account"))
        except:
            messages.error(request,"Failed to Delete Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_account"))

def admin_send_notification_parent(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    parents=Parents.objects.all()
    notification=NotificationParents.objects.all()
    return render(request,"hod_template/parent_notification.html",{"parents":parents,"admin":admin,"notification":notification})

def delete_parent_notifications(request,id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=NotificationParents.objects.get(id=id)
            mv.delete()
            messages.success(request,"Successfully Deleted Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_parent"))
        except:
            messages.error(request,"Failed to Delete Notification")
            return HttpResponseRedirect(reverse("admin_send_notification_parent"))

def add_parent(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    students=Students.objects.all()
    return render(request,"hod_template/add_parent_template.html",{"students":students,"admin":admin})

def add_parent_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        student=request.POST.get("student")
        default_profile_pic="/media/default.png"
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=4)
            if profile_pic_url!=None:
                user.parents.profile_pic=profile_pic_url
            else:
                user.parents.profile_pic=default_profile_pic
            student_obj=Students.objects.get(id=student)
            user.parents.student_id=student_obj
            user.save()
            messages.success(request,"Successfully Added Parent")
            return HttpResponseRedirect(reverse("add_parent"))
        except:
            messages.error(request,"Failed to Add Parent")
            return HttpResponseRedirect(reverse("add_parent"))

def edit_parent(request,parent_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    parent=Parents.objects.get(admin=parent_id)
    students=Students.objects.all()
    return render(request,"hod_template/edit_parent_template.html",{"parent":parent,"admin":admin,"students":students})


def edit_parent_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        parent_id=request.POST.get("parent_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        student=request.POST.get("student")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.get(id=parent_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()
            parent=Parents.objects.get(admin=parent_id)
            if profile_pic_url!=None:
                parent.profile_pic=profile_pic_url
            student_obj=Students.objects.get(id=student)
            parent.student_id=student_obj
            parent.save()
            messages.success(request,"Successfully Edited Parent")
            return HttpResponseRedirect(reverse("manage_parent"))
        except:
            messages.error(request,"Failed to Edit Parent")
            return HttpResponseRedirect(reverse("edit_parent",kwargs={"parent_id":parent_id}))

def delete_parent(request,parent_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=parent_id)
            user.delete()
            messages.success(request,"Successfuly Deleted Parent")
            return HttpResponseRedirect(reverse("manage_parent"))
        except:
            messages.error(request,"Failed to Delete Parent")
            return HttpResponseRedirect(reverse("manage_parent"))

def manage_parent(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    parents=Parents.objects.all()
    return render(request,"hod_template/manage_parent_template.html",{"parents":parents,"admin":admin})

def manage_pnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=PNews.objects.all()
    return render(request,"hod_template/manage_pnews.html",{"news":news,"admin":admin})

def add_pnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_pnews_template.html",{"admin":admin})

def add_pnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=PNews(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfuly Added News")
            return HttpResponseRedirect(reverse("manage_pnews"))
        except:
            messages.error(request,"Failed to Add News")
            return HttpResponseRedirect(reverse("manage_pnews"))

def view_pnews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=PNews.objects.get(id=news_id)
    comment=PComment.objects.filter(PNews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_pnews.html",{"news":news,"comment":comment,"admin":admin,"comment_count":comments_count,"staff":staff})

def edit_pnews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(PNews.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Failed to Edit News")
        return HttpResponseRedirect(reverse("manage_pnews"))
    news=PNews.objects.get(id=news_id)
    return render(request,"hod_template/edit_pnews_template.html",{"news":news,"admin":admin})

def edit_pnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=PNews.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Successfully Edited News")
            return HttpResponseRedirect(reverse("manage_pnews"))
        except:
            messages.error(request,"Failed to Edit News")
            return HttpResponseRedirect(reverse("manage_pnews"))

def delete_pnews(request,news_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=PNews.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Successfully Deleted News")
            return HttpResponseRedirect(reverse("manage_pnews"))
        except:
            messages.error(request,"Failed to Delete News")
            return HttpResponseRedirect(reverse("manage_pnews"))

# POST TEACHER COMMENT
def view_parent_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_pnews"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = PComment.objects.get(id=reply_id)
        try:
            Pcomment=PComment(PNews_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            Pcomment.save()
            messages.success(request, "Successfully saved Comment")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":News}))
        except:
            messages.error(request, "Failed to save Comment")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":News}))
# EDIT TEACHER COMMENT
def view_parent_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_pnews"))
    else:
        comment_id = request.POST.get("comment_id")
        TNews = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = PComment.objects.get(id=comment_id)
            comment.PNews_id=TNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Successfully Edited Comment")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Failed to Edit Comment")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":TNews}))

def delete_pcomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=PComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Successfully Deleted Comment")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":news_id}))

@csrf_exempt
def send_student_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    student=Students.objects.get(admin=id)
    notification=NotificationStudent(student_id=student,message=message)
    notification.save()
    return HttpResponse("True")

@csrf_exempt
def send_staff_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    staff=Staffs.objects.get(admin=id)
    notification=NotificationStaffs(staff_id=staff,message=message)
    notification.save()
    return HttpResponse("True")

@csrf_exempt
def send_parent_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    parent=Parents.objects.get(admin=id)
    notification=NotificationParents(parent_id=parent,message=message)
    notification.save()
    return HttpResponse("True")
    
@csrf_exempt
def send_account_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    account=Accounts.objects.get(admin=id)
    notification=NotificationAccounts(account_id=account,message=message)
    notification.save()
    return HttpResponse("True")

def covid19(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/covid19.html",{"admin":admin})
    
class InvoiceListView(View):
    def get(self, *args, **kwargs):
        invoices = Invoice.objects.all()
        context = {
            "invoices":invoices,
        }

        return render(self.request, 'hod_template/manage_invoice_template.html', context)
    
    def post(self, request):        
        # import pdb;pdb.set_trace()
        invoice_ids = request.POST.getlist("invoice_id")
        invoice_ids = list(map(int, invoice_ids))

        update_status_for_invoices = int(request.POST['status'])
        invoices = Invoice.objects.filter(id__in=invoice_ids)
        # import pdb;pdb.set_trace()
        if update_status_for_invoices == 0:
            invoices.update(status=False)
        else:
            invoices.update(status=True)

        return redirect('manage_invoice')





def createInvoice(request):
    """
    Invoice Generator page it will have Functionality to create new invoices, 
    this will be protected view, only admin has the authority to read and make
    changes here..
    """

    heading_message = 'Formset Demo'
    if request.method == 'GET':
        formset = LineItemFormset(request.GET or None)
        form = InvoiceForm(request.GET or None)
    elif request.method == 'POST':
        formset = LineItemFormset(request.POST)
        form = InvoiceForm(request.POST)
        
        if form.is_valid():
            invoice = Invoice.objects.create(student=form.data["student"],
                    student_email=form.data["student_email"],
                    billing_address=form.data["billing_address"],
                    date=form.data["date"],
                    due_date=form.data["due_date"],
                    message=form.data["message"],
                    paid=form.data["paid"],
                    balance=form.data["balance"]
            )
            # invoice.save()
            
        if formset.is_valid():
            # import pdb;pdb.set_trace()
            # extract name and other data from each form and save
            total = 0
            for form in formset:
                service = form.cleaned_data.get('service')
                description = form.cleaned_data.get('description')
                quantity = form.cleaned_data.get('quantity')
                rate = form.cleaned_data.get('rate')
                if service and description and quantity and rate:
                    amount = float(rate) * float(quantity)
                    total += amount
                    LineItem(
                        student=invoice,
                        service=service,
                        description=description,
                        quantity=quantity,
                        rate=rate,
                        amount=amount
                    ).save()
            invoice.total_amount = total
            invoice.save()
            try:
                generate_PDF(request, id=invoice.id)
            except Exception as e:
                print(f"********{e}********")
            return redirect('manage_invoice')  # Redirect to manage_invoice URL
    context = {
        "title": "Invoice Generator",
        "formset": formset,
        "form": form,
    }
    return render(request, 'hod_template/invoice-create.html', context)




def view_PDF(request, id=None):
    invoice = get_object_or_404(Invoice, id=id)
    lineitem = invoice.lineitem_set.all()

    context = {
        "company": {
            "name": "Eldo Valley Baptist Academy",
            "address" :"2348 Eldoret",
            "phone": "(010) 188 5662",
            "email": "eldovalleybaptistacademy@gmail.com",
        },
        "invoice_id": invoice.id,
        "invoice_total": invoice.total_amount,
        "student": invoice.student,
        "student_email": invoice.student_email,
        "date": invoice.date,
        "due_date": invoice.due_date,
        "billing_address": invoice.billing_address,
        "message": invoice.message,
        "lineitem": lineitem,
        "paid": invoice.paid,
        "balance": invoice.balance,

    }
    return render(request, 'hod_template/pdf_template.html', context)

def generate_PDF(request, id):
    # Use False instead of output path to save pdf to a variable
    pdf = pdfkit.from_url(request.build_absolute_uri(reverse('invoice_detail', args=[id])), False)
    response = HttpResponse(pdf,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    return response


def add_financial_record(request):
    user = CustomUser.objects.get(id=request.user.id)
    records = FinancialRecord.objects.all()
    students = CustomUser.objects.filter(user_type=3)

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        date = request.POST.get("date")
        fee_type = request.POST.get("fee_type")
        amount_paid = Decimal(request.POST.get("amount_paid"))  # Convert to Decimal

        try:
            student_user = CustomUser.objects.get(id=student_id)
            student = Students.objects.get(admin=student_user)

            # Retrieve the latest financial record for the student, regardless of the fee type
            latest_record = FinancialRecord.objects.filter(student=student).latest('created_at')
            fee_balance = latest_record.new_balance

            # Calculate the new balance by subtracting the amount paid from the fee_balance
            new_balance = fee_balance - amount_paid

            # Retrieve the latest new_balance regardless of the fee type
            latest_new_balance = FinancialRecord.objects.filter(student=student).latest('created_at').new_balance

            # Retrieve the default fees and date from the DefaultSettings model
            try:
                default_settings = DefaultSettings.objects.first()
                default_fees = {
                    'lunch': default_settings.lunch_fee,
                    'transport': default_settings.transport_fee,
                    'tuition': default_settings.tuition_fee,
                    'transport and lunch': default_settings.transport_and_lunch_fee,
                    'tuition and transport': default_settings.tuition_and_transport_fee,
                    'tuition and lunch': default_settings.tuition_and_lunch_fee,
                    'tuition, lunch and transport': default_settings.tuition_lunch_transport_fee,
                    'other': default_settings.other_fee,
                }
                default_time = default_settings.default_time.strftime('%Y-%m-%d')
            except DefaultSettings.DoesNotExist:
                default_fees = {
                    'lunch': 1000,
                    'transport': 2000,
                    'tuition': 100000,
                    'transport and lunch': 0,
                    'tuition and transport': 0,
                    'tuition and lunch': 0,
                    'tuition, lunch and transport': 0,
                    'other': 0,
                }
                default_time = "2023-06-16 15:46:00"  # Set the default date as per your requirement

            # Add the default fee for the selected fee type and the latest new_balance
            fee_balance = default_fees.get(fee_type, 0) + latest_new_balance
            new_balance = fee_balance - amount_paid

            # Create the financial record
            record = FinancialRecord.objects.create(
                student=student,
                date=date,
                fee_type=fee_type,
                fee_balance=fee_balance,
                amount_paid=amount_paid,
                new_balance=new_balance
            )

            # Redirect or display a success message
            return HttpResponseRedirect(reverse("financial_record_list"))
        except Students.DoesNotExist:
            error_message = "Failed to add financial record. Student with ID {} not found.".format(student_id)
            return HttpResponse(error_message)
        except FinancialRecord.DoesNotExist:
            # If no previous record exists for the student, set fee_balance to the default fee for the selected fee type
            default_fees = {
                'lunch': 1000,
                'transport': 2000,
                'tuition': 100000,
                'transport and lunch': 0,
                'tuition and transport': 0,
                'tuition and lunch': 0,
                'tuition, lunch and transport': 0,
                'other': 0,
            }
            fee_balance = default_fees.get(fee_type, 0)

            # Calculate the new balance by subtracting the amount paid from the fee_balance
            new_balance = fee_balance - amount_paid

            # Create the financial record
            record = FinancialRecord.objects.create(
                student=student,
                date=date,
                fee_type=fee_type,
                fee_balance=fee_balance,
                amount_paid=amount_paid,
                new_balance=new_balance
            )

            # Redirect or display a success message
            return HttpResponseRedirect(reverse("financial_record_list"))
        except Exception as e:
            error_message = "Failed to add financial record. Error: {}".format(str(e))
            return HttpResponse(error_message)

    else:
        try:
            default_settings = DefaultSettings.objects.first()
            if default_settings is not None:
                default_fees = {
                    'lunch': default_settings.lunch_fee,
                    'transport': default_settings.transport_fee,
                    'tuition': default_settings.tuition_fee,
                    'transport and lunch': default_settings.transport_and_lunch_fee,
                    'tuition and transport': default_settings.tuition_and_transport_fee,
                    'tuition and lunch': default_settings.tuition_and_lunch_fee,
                    'tuition, lunch and transport': default_settings.tuition_lunch_transport_fee,
                    'other': default_settings.other_fee,
                }
                default_time = default_settings.default_time.strftime('%Y-%m-%d')
            else:
                # Create new default settings with default values
                default_settings = DefaultSettings.objects.create(
                    lunch_fee=1000,
                    transport_fee=2000,
                    tuition_fee=100000,
                    transport_and_lunch_fee=0,
                    tuition_and_transport_fee=0,
                    tuition_and_lunch_fee=0,
                    tuition_lunch_transport_fee=0,
                    other_fee=0
                )
                default_fees = {
                    'lunch': default_settings.lunch_fee,
                    'transport': default_settings.transport_fee,
                    'tuition': default_settings.tuition_fee,
                    'transport and lunch': default_settings.transport_and_lunch_fee,
                    'tuition and transport': default_settings.tuition_and_transport_fee,
                    'tuition and lunch': default_settings.tuition_and_lunch_fee,
                    'tuition, lunch and transport': default_settings.tuition_lunch_transport_fee,
                    'other': default_settings.other_fee,
                }
                default_time = default_settings.default_time.strftime('%Y-%m-%d')
        except DefaultSettings.DoesNotExist:
            # Create new default settings with default values
            default_settings = DefaultSettings.objects.create(
                lunch_fee=1000,
                transport_fee=2000,
                tuition_fee=100000,
                transport_and_lunch_fee=0,
                tuition_and_transport_fee=0,
                tuition_and_lunch_fee=0,
                tuition_lunch_transport_fee=0,
                other_fee=0
            )
            default_fees = {
                'lunch': default_settings.lunch_fee,
                'transport': default_settings.transport_fee,
                'tuition': default_settings.tuition_fee,
                'transport and lunch': default_settings.transport_and_lunch_fee,
                'tuition and transport': default_settings.tuition_and_transport_fee,
                'tuition and lunch': default_settings.tuition_and_lunch_fee,
                'tuition, lunch and transport': default_settings.tuition_lunch_transport_fee,
                'other': default_settings.other_fee,
            }
            default_time = default_settings.default_time.strftime('%Y-%m-%d')# Set the default date as per your requirement
    
        return render(request, "hod_template/financial_record_add.html", {"students": students, "default_fees": default_fees, "default_time": default_time})




def delete_financial_record(request, record_id):
    # Retrieve the financial record object
    financial_record = get_object_or_404(FinancialRecord, id=record_id)

    if request.method == 'POST':
        # Delete the financial record
        financial_record.delete()
        messages.success(request, "Financial record deleted successfully")
        return redirect('financial_record_list')

    # If the request is not a POST, render the confirmation template
    return render(request, "hod_template/confirm_delete_record.html", {"financial_record": financial_record})
    
def confirm_delete_record(request, record_id):
    try:
        record = FinancialRecord.objects.get(id=record_id)
        return render(request, 'hod_template/confirm_delete_record.html', {'record': record})
    except FinancialRecord.DoesNotExist:
        messages.error(request, 'Financial record not found.')
        return redirect('financial_record_list')


def default_settings(request):
    # Retrieve the existing default settings if they exist
    try:
        default_settings = DefaultSettings.objects.first()
    except DefaultSettings.DoesNotExist:
        default_settings = None
    
    # Render the default settings form template with the default settings data
    return render(request, 'hod_template/default_settings.html', {'default_settings': default_settings})




def save_default_settings(request):
    if request.method == 'POST':
        # Retrieve the form data
        lunch = Decimal(request.POST.get('lunch'))
        transport = Decimal(request.POST.get('transport'))
        tuition = Decimal(request.POST.get('tuition'))
        default_time = timezone.localtime(timezone.now()).date()  # Set the default_time to the current local date

        # Save the default settings to the database
        try:
            with transaction.atomic():
                default_settings = DefaultSettings.objects.first()
                if default_settings:
                    # Update existing default settings
                    default_settings.lunch_fee = lunch
                    default_settings.transport_fee = transport
                    default_settings.tuition_fee = tuition
                    default_settings.default_time = default_time  # Update the default_time field
                    default_settings.save()
                else:
                    # Create new default settings
                    default_settings = DefaultSettings.objects.create(
                        lunch_fee=lunch,
                        transport_fee=transport,
                        tuition_fee=tuition,
                        default_time=default_time  # Add the default_time field
                    )

                # Create financial records for all students
                students = Students.objects.all()
                for student in students:
                    # Get the latest financial record for the student
                    try:
                        latest_record = FinancialRecord.objects.filter(student=student).latest('created_at')
                        fee_balance = latest_record.new_balance + default_settings.tuition_fee
                        new_balance =fee_balance-0
                    except FinancialRecord.DoesNotExist:
                        # Create a new record if no previous record exists for the student
                        fee_balance= default_settings.tuition_fee
                        new_balance = default_settings.tuition_fee

                    FinancialRecord.objects.create(
                        student=student,
                        date=default_time,  # Use default_time as the date for financial records
                        fee_type='tuition',  # Set the fee_type to a default value or adjust as needed
                        amount_paid=0,  # Set the amount_paid to a default value or adjust as needed
                        fee_balance=fee_balance ,  # Set fee_balance to new_balance if it exists, otherwise 0
                        new_balance=new_balance  # Set the new_balance to a default value or adjust as needed
                    )

        except Exception as e:
            # Handle any exceptions that may occur during saving
            error_message = "Failed to save default settings. Error: {}".format(str(e))
            return HttpResponse(error_message)

        # Redirect to the default settings form with a success message
        messages.success(request, "Successfully saved Fee Structure")
        return redirect('add_financial_record')

    # If the request is not a POST, redirect to the default settings form
    return redirect('default_settings')



def financial_record_list(request):
    financial_records = FinancialRecord.objects.all().select_related('student__admin')

    return render(request, "hod_template/financial_record_list.html", {"financial_records": financial_records})
    


def generate_receipt_pdf(request, record_id):
    try:
        record = FinancialRecord.objects.get(id=record_id)
    except FinancialRecord.DoesNotExist:
        return HttpResponse("Financial record does not exist")

    # Prepare data for the receipt
    context = {
        "company": {
            "name": "Eldo Valley Baptist Academy",
            "address" :"2348 Eldoret",
            "phone": "(010) 188 5662",
            "email": "eldovalleybaptistacademy@gmail.com",
        },
        'record': record
    }

    # Render the receipt template with the data
    template = get_template('hod_template/receipt_template.html')
    receipt_content = template.render(context)

    # Generate PDF from the receipt content
    pdf = generate_pdf(receipt_content)

    # Create an HTTP response with the PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    response.write(pdf)

    return response

def generate_pdf(content):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file"
    pisa.CreatePDF(content, dest=buffer)

    # Get the value of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf



def generate_receipt_pdfs(request, student_id):
    try:
        records = FinancialRecord.objects.filter(student__id=student_id)
    except FinancialRecord.DoesNotExist:
        return HttpResponse("Financial records do not exist for the student")

    # Prepare data for the receipts
    context = {
        'records': records,
        "company": {
            "name": "Eldo Valley Baptist Academy",
            "address" :"2348 Eldoret",
            "phone": "(010) 188 5662",
            "email": "eldovalleybaptistacademy@gmail.com",
        }
    }

    # Render the receipt template with the data
    template = get_template('hod_template/receipt_all_records_template.html')
    receipt_content = template.render(context)

    # Generate PDF from the receipt content
    pdf = generate_pdf(receipt_content)

    # Create an HTTP response with the PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipts.pdf"'
    response.write(pdf)

    return response


def generate_pdfs(content):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file"
    pisa.CreatePDF(content, dest=buffer)

    # Get the value of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
    


def update_session_year(request):
    if request.method == "POST":
        new_session_year_id = request.POST.get("new_session_year")

        # Update the session year ID of all students
        Students.objects.update(session_year_id=new_session_year_id)

        return redirect('students_list')  # Redirect to the students list page or any other page you prefer

    session_years = SessionYearModel.object.all()
    return render(request, 'hod_template/change_session_year.html', {'session_years': session_years})

    
def students_list(request):
    # Retrieve the list of students
    students = Students.objects.all()
    
    # Render the students list template with the students data
    return render(request, 'hod_template/students_list.html', {'students': students})

















