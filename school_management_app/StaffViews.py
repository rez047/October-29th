import json
from datetime import datetime
from uuid import uuid4

from django.contrib import messages
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404

import datetime
import traceback

from school_management_app.models import Subjects, SessionYearModel, Students, Attendance, AttendanceReport, \
    LeaveReportStaff, Staffs, FeedBackStaffs, CustomUser, Courses, NotificationStaffs, StudentResult, TNews, TComment


def staff_home(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    course_id_list=[]
    for subject in subjects:
        course=Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)

    final_course=[]
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count=Students.objects.filter(course_id__in=final_course).count()
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()

    staff=Staffs.objects.get(admin=request.user.id)
    leave_count=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
    subject_count=subjects.count()

    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance=Students.objects.filter(course_id__in=final_course)
    student_list=[]
    student_list_attendance_present=[]
    student_list_attendance_absent=[]
    for student in students_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True,student_id=student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False,student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/staff_home_template.html",{"notifications":notifications,"students_count":students_count,"staff_pro":staff_pro,"attendance_count":attendance_count,"leave_count":leave_count,"subject_count":subject_count,"subject_list":subject_list,"attendance_list":attendance_list,"student_list":student_list,"present_list":student_list_attendance_present,"absent_list":student_list_attendance_absent})

def staff_take_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.object.all()
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/staff_take_attendance.html",{"notifications":notifications,"subjects":subjects,"session_years":session_years,"staff_pro":staff_pro})

@csrf_exempt
def get_students(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.object.get(id=session_year)
    students=Students.objects.filter(course_id=subject.course_id,session_year_id=session_model)
    list_data=[]

    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    subject_id=request.POST.get("subject_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")

    subject_model=Subjects.objects.get(id=subject_id)
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_model=SessionYearModel.object.get(id=session_year_id)
    json_sstudent=json.loads(student_ids)
    #print(data[0]['id'])


    try:
        attendance=Attendance(subject_id=subject_model,attendance_date=attendance_date,session_year_id=session_model)
        attendance.save()

        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport(student_id=student,attendance_id=attendance,status=stud['status'])
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR")

def staff_update_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.object.all()
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/staff_update_attendance.html",{"notifications":notifications,"subjects":subjects,"staff_pro":staff_pro,"session_year_id":session_year_id})

@csrf_exempt
def get_attendance_dates(request):
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
def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_updateattendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    json_sstudent=json.loads(student_ids)


    try:
        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
             attendance_report.status=stud['status']
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR")

def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data=LeaveReportStaff.objects.filter(staff_id=staff_obj)
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/staff_apply_leave.html",{"notifications":notifications,"leave_data":leave_data,"staff_pro":staff_pro})

def staff_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_apply_leave"))
    else:
        leave_start_date=request.POST.get("leave_start_date")
        leave_end_date=request.POST.get("leave_end_date")
        leave_msg=request.POST.get("leave_msg")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStaff(staff_id=staff_obj,leave_start_date=leave_start_date,leave_end_date=leave_end_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))
        except:
            messages.error(request, "Failed to Apply for Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))


def staff_feedback(request):
    staff_id=Staffs.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaffs.objects.filter(staff_id=staff_id)
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    staff_notifcation=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff_notifcation.id)
    return render(request,"staff_template/staff_feedback.html",{"feedback_data":feedback_data,"staff":staff,"notifications":notifications})

def staff_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaffs(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))
        except:
            messages.error(request, "Failed to Send Feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))

def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    return render(request,"staff_template/staff_profile.html",{"user":user,"staff":staff})

def staff_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_profile"))
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

            staff=Staffs.objects.get(admin=customuser.id)
            staff.address=address
            if profile_pic_url!=None:
                staff.profile_pic=profile_pic_url
            staff.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("staff_profile"))

            
def staff_news(request):
    news=TNews.objects.all().order_by('-ndate')
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    staff_notifcation=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff_notifcation.id)
    return render(request, "staff_template/staff_news.html",{"news":news,"staff":staff,"notifications":notifications})


def view_staff_news(request, news_id):
    news=TNews.objects.get(id=news_id)
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    comment=TComment.objects.filter(TNews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    staff_notifcation=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff_notifcation.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request, "staff_template/view_staff_news.html",{"news":news,"notifications":notifications,"staff_pro":staff_pro,"comment":comment,"comment_count":comments_count,"staff":staff})

    # Comment
def view_staff_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_news"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = TComment.objects.get(id=reply_id)
        try:
            comment=TComment(TNews_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            comment.save()
            messages.success(request, "Successfully Posted Comment")
            return HttpResponseRedirect(reverse("view_staff_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Failed to Post Comment")
            return HttpResponseRedirect(reverse("view_staff_news",kwargs={"news_id":News}))
# EDIT
def view_staff_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("staff_news"))
    else:
        comment_id = request.POST.get("comment_id")
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = TComment.objects.get(id=comment_id)
            comment.TNews_id=News
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Successfully Edited Comment")
            return HttpResponseRedirect(reverse("view_staff_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_staff_news",kwargs={"news_id":News}))


def delete_tcomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=TComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Successfully Deleted Comment")
            return HttpResponseRedirect(reverse("view_staff_news",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Failed to Delete Comment")
            return HttpResponseRedirect(reverse("view_staff_news",kwargs={"news_id":news_id}))


@csrf_exempt
def staff_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        staff=Staffs.objects.get(admin=request.user.id)
        staff.fcm_token=token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def staff_all_notification(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/all_notification.html",{"notifications":notifications,"staff_pro":staff_pro})

def staff_add_result(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.object.all()
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/staff_add_result.html",{"notifications":notifications,"subjects":subjects,"session_years":session_years,"staff_pro":staff_pro})


def save_student_result(request):
    if request.method != 'POST':
        return HttpResponseRedirect('staff_add_result')

    student_admin_ids = request.POST.getlist('student_list')
    assignment_marks = request.POST.get('assignment_marks')
    exam_marks = request.POST.get('exam_marks')
    subject_id = request.POST.get('subject')

    subject_obj = Subjects.objects.get(id=subject_id)

    try:
        results_added = 0

        for student_admin_id in student_admin_ids:
            student_obj = Students.objects.get(admin=student_admin_id)
            result = StudentResult.objects.create(
                student_id=student_obj,
                subject_id=subject_obj,
                subject_assignment_marks=assignment_marks,
                subject_exam_marks=exam_marks
            )
            results_added += 1

        if results_added > 0:
            messages.success(request, f"Successfully added {results_added} results")
        else:
            messages.info(request, "No results were added")

        return HttpResponseRedirect(reverse("staff_add_result"))

    except Exception as e:
        messages.error(request, f"Failed to save results: {str(e)}")
        return HttpResponseRedirect(reverse("staff_add_result"))



@csrf_exempt
def get_course_name(request):
    if request.method == "POST" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        subject=Subjects.objects.get(id=subject_id)
        subject.course_id=course_id
        course_id = request.POST.get("course_id")
        course = get_object_or_404(Courses, id=course_id)
        course_name = course.course_name
        return JsonResponse({"course_name": course_name,"id":subject_id})
    else:
        return JsonResponse({"error": "Invalid request"})



@csrf_exempt
def fetch_result_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        
        results = StudentResult.objects.filter(student_id=student_id, subject_id=subject_id)
        
        data = []
        for result in results:
            result_data = {
                'assignment_marks': result.subject_assignment_marks,
                'exam_marks': result.subject_exam_marks
            }
            data.append(result_data)
        
        return JsonResponse(data, safe=False)
        
def staff_success_page(request):
    return render(request, 'staff_template/success_page.html')

def tcovid19(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff_pro=Staffs.objects.get(admin=user)
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/covid19.html",{"notifications":notifications,"staff_pro":staff_pro})
    

