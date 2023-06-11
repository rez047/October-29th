from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from school_management_app.forms import EditResultForm
from school_management_app.models import Students, Subjects, StudentResult, CustomUser, Staffs

class EditResultViewClass(View):
    def get(self, request, *args, **kwargs):
        staff_id = request.user.id
        edit_result_form = EditResultForm(staff_id=staff_id)
        user = CustomUser.objects.get(id=request.user.id)
        staff_pro = Staffs.objects.get(admin=user)
        return render(request, "staff_template/edit_student_result.html", {"form": edit_result_form, "staff_pro": staff_pro})

    def post(self, request, *args, **kwargs):
        form = EditResultForm(staff_id=request.user.id, data=request.POST)
        if form.is_valid():
            student_admin_ids = form.cleaned_data['student_ids']
            assignment_marks = form.cleaned_data['assignment_marks']
            exam_marks = form.cleaned_data['exam_marks']
            subject_id = form.cleaned_data['subject_id']

            for student_admin_id in student_admin_ids:
                student_obj = Students.objects.get(admin=student_admin_id)
                subject_obj = Subjects.objects.get(id=subject_id)
                results = StudentResult.objects.filter(subject_id=subject_obj, student_id=student_obj)
                if results:
                    # Render a template with the list of results for the staff to choose from
                    return render(request, "staff_template/choose_result.html", {"results": results, "assignment_marks": assignment_marks, "exam_marks": exam_marks})

            messages.error(request, "No Results found for the selected student(s) and subject.")
            return HttpResponseRedirect(reverse("edit_student_result"))
        else:
            messages.error(request, "Failed to Update Results")
            form = EditResultForm(request.POST, staff_id=request.user.id)
            user = CustomUser.objects.get(id=request.user.id)
            staff_pro = Staffs.objects.get(admin=user)
            return render(request, "staff_template/edit_student_result.html", {"form": form, "staff_pro": staff_pro})



class UpdateSelectedResultView(View):
    def post(self, request, *args, **kwargs):
        result_id = request.POST.get('result_id')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')

        # Update the selected result based on the provided information
        try:
            result = StudentResult.objects.get(id=result_id)
            result.subject_assignment_marks = assignment_marks
            result.subject_exam_marks = exam_marks
            result.save()
            # Redirect to a success page or return a success message
            return HttpResponseRedirect(reverse('staff_template/success_page'))
        except StudentResult.DoesNotExist:
            # Handle the case where the result is not found
            return render(request, 'result_not_found.html')



