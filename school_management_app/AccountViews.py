import json
import requests
from datetime import datetime
from uuid import uuid4

from django.contrib import messages
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from django.db.models import Sum
from decimal import Decimal
import pdfkit
import datetime
import io
from xhtml2pdf import pisa

from school_management_app.forms import  InvoiceForm,LineItemFormset
from school_management_app.models import LeaveReportAccount, Accounts, FeedBackAccounts, CustomUser, NotificationAccounts, ANews, AComment, Invoice, LineItem, FinancialRecord, Students

def account_home(request):
    return render(request,"account_template/account_home_template.html")
    
    
def account_apply_leave(request):
    account_obj = Accounts.objects.get(admin=request.user.id)
    leave_data=LeaveReportAccount.objects.filter(account_id=account_obj)
    user=CustomUser.objects.get(id=request.user.id)
    account_pro=Accounts.objects.get(admin=user)
    account=Accounts.objects.get(admin=request.user.id)
    notifications=NotificationAccounts.objects.filter(account_id=account.id)
    return render(request,"account_template/account_apply_leave.html",{"notifications":notifications,"leave_data":leave_data,"account_pro":account_pro})

def account_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("account_apply_leave"))
    else:
        leave_start_date=request.POST.get("leave_start_date")
        leave_end_date=request.POST.get("leave_end_date")
        leave_msg=request.POST.get("leave_msg")

        account_obj=Accounts.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportAccount(account_id=account_obj,leave_start_date=leave_start_date,leave_end_date=leave_end_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully applied leave")
            return HttpResponseRedirect(reverse("account_apply_leave"))
        except:
            messages.error(request, "Failed to apply leave")
            return HttpResponseRedirect(reverse("account_apply_leave"))


@csrf_exempt
def account_feedback(request):
    account_id=Accounts.objects.get(admin=request.user.id)
    feedback_data=FeedBackAccounts.objects.filter(account_id=account_id)
    user=CustomUser.objects.get(id=request.user.id)
    account=Accounts.objects.get(admin=user)
    account_notifcation=Accounts.objects.get(admin=request.user.id)
    notifications=NotificationAccounts.objects.filter(account_id=account_notifcation.id)
    return render(request,"account_template/account_feedback.html",{"feedback_data":feedback_data,"account":account,"notifications":notifications})

@csrf_exempt
def account_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("account_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        account_obj=Accounts.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackAccounts(account_id=account_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully sent Feedback")
            return HttpResponseRedirect(reverse("account_feedback"))
        except:
            messages.error(request, "Failed to send Feedback")
            return HttpResponseRedirect(reverse("account_feedback"))

def account_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    account=Accounts.objects.get(admin=user)
    account_notifcation=Accounts.objects.get(admin=request.user.id)
    notifications=NotificationAccounts.objects.filter(account_id=account_notifcation.id)
    return render(request,"account_template/account_profile.html",{"notifications":notifications,"user":user,"account":account})

def account_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("account_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        address=request.POST.get("address")
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
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            account=Accounts.objects.get(admin=customuser)
            account.address=address
            if profile_pic_url!=None:
                account.profile_pic=profile_pic_url
            account.save()
            messages.success(request, "Successfully Edited Profile")
            return HttpResponseRedirect(reverse("account_profile"))
        except:
            messages.error(request, "Failed to Edit Profile")
            return HttpResponseRedirect(reverse("account_profile"))

def account_news(request):
    news=ANews.objects.all().order_by('-ndate')
    user=CustomUser.objects.get(id=request.user.id)
    account=Accounts.objects.get(admin=user)
    account_notifcation=Accounts.objects.get(admin=request.user.id)
    notifications=NotificationAccounts.objects.filter(account_id=account_notifcation.id)
    return render(request, "account_template/account_news.html",{"news":news,"account":account,"notifications":notifications})

def view_account_news(request, news_id):
    news=ANews.objects.get(id=news_id)
    user=CustomUser.objects.get(id=request.user.id)
    account=Accounts.objects.get(admin=user)
    comment=AComment.objects.filter(ANews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    account_notifcation=Accounts.objects.get(admin=request.user.id)
    notifications=NotificationAccounts.objects.filter(account_id=account_notifcation.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request, "account_template/view_account_news.html",{"news":news,"notifications":notifications,"account":account,"comment":comment,"comment_count":comments_count,"staff":staff})
# POST COMMENT
    # Comment
def view_account_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("account_news"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = AComment.objects.get(id=reply_id)
        try:
            comment=AComment(ANews_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            comment.save()
            messages.success(request, "Successfully Posted Comment")
            return HttpResponseRedirect(reverse("view_account_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Failed to Post Comment")
            return HttpResponseRedirect(reverse("view_account_news",kwargs={"news_id":News}))
# EDIT
def view_account_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("account_news"))
    else:
        comment_id = request.POST.get("comment_id")
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = AComment.objects.get(id=comment_id)
            comment.ANews_id=News
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Successfully Edited Comment!")
            return HttpResponseRedirect(reverse("view_account_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Failed to Edit Comment")
            return HttpResponseRedirect(reverse("view_account_news",kwargs={"news_id":News}))


def delete_acomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=AComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Successfully Deleted Comment")
            return HttpResponseRedirect(reverse("view_account_news",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_account_news",kwargs={"news_id":news_id}))

@csrf_exempt
def account_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        account=Accounts.objects.get(admin=request.user.id)
        account.fcm_token=token
        account.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def account_all_notification(request):
    user=CustomUser.objects.get(id=request.user.id)
    account=Accounts.objects.get(admin=user)
    account=Accounts.objects.get(admin=request.user.id)
    notifications=NotificationAccounts.objects.filter(account_id=account.id)
    return render(request,"account_template/all_notification.html",{"notifications":notifications,"account":account})
    
def account_add_financial_record(request):
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

            # Retrieve the latest financial record for the student
            try:
                latest_record = FinancialRecord.objects.filter(student=student).latest('created_at')
                fee_balance = latest_record.new_balance
            except FinancialRecord.DoesNotExist:
                # If no previous record exists, set fee_balance to 0
                fee_balance = 0

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
            return HttpResponseRedirect(reverse("account_financial_record_list"))
        except CustomUser.DoesNotExist:
            error_message = "Failed to add financial record. Student with ID {} not found.".format(student_id)
            return HttpResponse(error_message)
        except Students.DoesNotExist:
            error_message = "Failed to add financial record. Student details not found for ID {}.".format(student_id)
            return HttpResponse(error_message)
        except FinancialRecord.DoesNotExist:
            error_message = "Failed to add financial record. No previous record found for the student."
            return HttpResponse(error_message)
        except Exception as e:
            error_message = "Failed to add financial record. Error: {}".format(str(e))
            return HttpResponse(error_message)

    else:
        return render(request, "account_template/financial_record_add.html", {"students": students, "records": records, })



def account_financial_record_list(request):
    financial_records = FinancialRecord.objects.all().select_related('student__admin')

    return render(request, "account_template/financial_record_list.html", {"financial_records": financial_records})

def account_generate_receipt_pdf(request, student_id):
    try:
        record = FinancialRecord.objects.filter(student__id=student_id).first()
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
    template = get_template('account_template/receipt_template.html')
    receipt_content = template.render(context)

    # Generate PDF from the receipt content
    pdf = account_generate_pdf(receipt_content)

    # Create an HTTP response with the PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    response.write(pdf)

    return response

def account_generate_pdf(content):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file"
    pisa.CreatePDF(content, dest=buffer)

    # Get the value of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf



def account_generate_receipt_pdfs(request, student_id):
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
    template = get_template('account_template/receipt_all_records_template.html')
    receipt_content = template.render(context)

    # Generate PDF from the receipt content
    pdf = account_generate_pdfs(receipt_content)

    # Create an HTTP response with the PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipts.pdf"'
    response.write(pdf)

    return response


def account_generate_pdfs(content):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file"
    pisa.CreatePDF(content, dest=buffer)

    # Get the value of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

