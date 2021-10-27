import os
from pprint import pprint

import pytz
from canvasapi.module import Module
from django.conf import settings
from canvasapi import Canvas, enrollment, assignment, submission
from django.utils.timezone import datetime
from classroom.models import Student, Assignment, Submission


def build_emails():
    q = Student.objects.filter(email__isnull=True, homeroom__contains="6")

    stu: Student
    for stu in q:
        stu.email = f"{stu.lname}{stu.fname[:2]}@lhprep.org".lower()
        stu.save()


def match_students():
    print("Match Students")
    canvas = Canvas("https://lhps.instructure.com", os.getenv("CANVAS_TOKEN", ""))

    course = canvas.get_course(settings.SIXTH_COURSE_ID)
    enrollments = course.get_enrollments()

    enr: enrollment.Enrollment
    for enr in enrollments:
        q = Student.objects.filter(email__iexact=enr.user.get("login_id"))
        if q.exists():
            stu = q.first()
            stu.canvas_id = enr.user_id
            stu.save()

    q = Student.objects.filter(canvas_id__isnull=True, homeroom__contains="6")
    missing_arr = [str(stu) for stu in q]
    print("Students without Canvas ID:", ", ".join(missing_arr))


def get_assignments():
    print("Get Assignments")
    canvas = Canvas("https://lhps.instructure.com", os.getenv("CANVAS_TOKEN", ""))

    course = canvas.get_course(settings.SIXTH_COURSE_ID)
    modules = course.get_modules()

    module: Module
    for module in modules:
        items = module.get_module_items()
        assignments = [i for i in items]

        for a in assignments:
            try:
                if "✴️" not in a.title and "⭐️" not in a.title: continue
                if not a.published: continue

                db_a, created = Assignment.objects.get_or_create(canvas_id=a.content_id)
                db_a.name = a.title
                db_a.module = module.name
                db_a.save()
            except Exception as e:
                print(e)
                print(repr(a))
                continue


def get_submissions():
    print("Get Submissions")
    canvas = Canvas("https://lhps.instructure.com", os.getenv("CANVAS_TOKEN", ""))

    course = canvas.get_course(settings.SIXTH_COURSE_ID)
    assignmets = course.get_assignments()

    a: assignment.Assignment
    for a in assignmets:
        subs = a.get_submissions()

        sub: submission.Submission
        for sub in subs:
            # pprint(repr(sub))
            try:
                if sub.workflow_state == "unsubmitted": continue

                q = Submission.objects.filter(student__canvas_id=sub.user_id, assignment__canvas_id=a.id)

                if q:
                    db_sub = q.first()
                else:
                    db_sub = Submission(canvas_id=sub.id)

                db_sub.student = Student.objects.get(canvas_id=sub.user_id)
                db_sub.assignment = Assignment.objects.get(canvas_id=a.id)
                db_sub.submitted_at = datetime.strptime(sub.submitted_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)

                if sub.grade:
                    db_sub.satisfactory = sub.grade != "incomplete"

                db_sub.save()
            except Exception as e:
                print(e)
                pprint(repr(sub))
                continue


def do_all():
    match_students()
    get_assignments()
    get_submissions()
