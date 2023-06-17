import datetime
import json
import os

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse
from django.template import loader
from django.template.loader import get_template
from django.views import View
from .forms import BulkInvoiceUploadForm

from school_management_app.EmailBackEnd import EmailBackEnd
from school_management_app.models import CustomUser, Courses, SessionYearModel, LineItem, Invoice
from school_management_system import settings
from school_management_app.forms import LineItemFormset, InvoiceForm

import pdfkit

def ShowLoginPage(request):
    return render(request,"login_page.html")



def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        email_or_username = request.POST.get("username")
        password = request.POST.get("password")
        user = None

        backend = EmailBackEnd()

        # Check if the input is an email
        if "@" in email_or_username:
            user = backend.authenticate(request, username=email, password=password)
        else:
            user = backend.authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("staff_home"))
            else:
                return HttpResponseRedirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")






def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def Testurl(request):
    return HttpResponse("Ok")

def signup_admin(request):
    return render(request,"signup_admin_page.html")

def signup_student(request):
    courses=Courses.objects.all()
    session_years=SessionYearModel.object.all()
    return render(request,"signup_student_page.html",{"courses":courses,"session_years":session_years})

def signup_staff(request):
    return render(request,"signup_staff_page.html")

def do_admin_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")
    default_profile_pic="/media/default.png"
    if request.FILES.get('profile_pic',False):
        profile_pic=request.FILES['profile_pic']
        fs=FileSystemStorage()
        filename=fs.save(profile_pic.name,profile_pic)
        profile_pic_url=fs.url(filename)
    else:
        profile_pic_url=None
    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=1)
        if profile_pic_url!=None:
            user.adminhod.profile_pic=profile_pic_url
        else:
            user.adminhod.profile_pic=default_profile_pic
        user.save()
        messages.success(request,"Successfully Created Admin")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Admin")
        return HttpResponseRedirect(reverse("show_login"))

def do_staff_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")
    address=request.POST.get("address")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=2)
        user.staffs.address=address
        user.save()
        messages.success(request,"Successfully Created Staff")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Staff")
        return HttpResponseRedirect(reverse("show_login"))

def do_signup_student(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")
    session_year_id = request.POST.get("session_year")
    course_id = request.POST.get("course")
    sex = request.POST.get("sex")
    default_profile_pic="/media/default.png"
    if request.FILES.get('profile_pic',False):
        profile_pic=request.FILES['profile_pic']
        fs=FileSystemStorage()
        filename=fs.save(profile_pic.name,profile_pic)
        profile_pic_url=fs.url(filename)
    else:
        profile_pic_url=None
    try:
        user = CustomUser.objects.create_user(username=username, password=password, email=email, last_name=last_name, first_name=first_name, user_type=3)
        user.students.address = address
        course_obj = Courses.objects.get(id=course_id)
        user.students.course_id = course_obj
        session_year = SessionYearModel.object.get(id=session_year_id)
        user.students.session_year_id = session_year
        user.students.gender = sex
        if profile_pic_url!=None:
            user.students.profile_pic = profile_pic_url
        else:
            user.students.profile_pic = default_profile_pic
        user.save()
        messages.success(request, "Successfully Added Student")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request, "Failed to Add Student")
        return HttpResponseRedirect(reverse("show_login"))
        
def bulk_upload(request):
    if request.method == 'POST':
        form = BulkInvoiceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            # Process the file and save the invoices to the database
            import pandas as pd

            try:
                df = pd.read_excel(file)
            except Exception as e:
                form.add_error('file', 'Error reading the file. Please provide a valid Excel file.')
                return render(request, 'hod_template/bulk_upload.html', {'form': form})

            for index, row in df.iterrows():
                student = row['Student']
                customer_email = row['Customer Email']
                billing_address = row['Billing Address']
                date = row['Date']
                due_date = row['Due Date']
                message = row['Message']
                total_amount = row['Total Amount']
                status = row['Status']
                paid = row['Paid']
                balance = row['Balance']

                invoice = Invoice(
                    student=student,
                    customer_email=customer_email,
                    billing_address=billing_address,
                    date=date,
                    due_date=due_date,
                    message=message,
                    total_amount=total_amount,
                    status=status,
                    paid=paid,
                    balance=balance
                )
                invoice.save()

            return render(request, 'hod_template/success_page.html')

    else:
        form = BulkInvoiceUploadForm()

    return render(request, 'hod_template/bulk_upload.html', {'form': form})


def success_page(request):
    return render(request, 'hod_template/success_page.html')


