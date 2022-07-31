import json
import re

from django.db import models

homerooms = (
    ("4A", "4A"),
    ("4B", "4B"),
    ("4C", "4C"),
    ("4D", "4D"),
    ("4E", "4E"),
    ("4F", "4F"),
    ("5A", "5A"),
    ("5B", "5B"),
    ("5C", "5C"),
    ("5D", "5D"),
    ("5E", "5E"),
    ("5F", "5F"),
    ("6A", "6 Q1 AM"),
    ("6B", "6 Q1 PM"),
    ("6C", "6 Q2 AM"),
    ("6D", "6 Q2 PM"),
    ("6E", "6 Q3 AM"),
    ("6F", "6 Q3 PM"),
    ("6G", "6 Q4 AM"),
    ("6H", "6 Q4 PM"),
    ("NA", "N/A"),
)


# Create your models here.
class Student(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    fname = models.TextField()
    lname = models.TextField()
    homeroom = models.CharField(max_length=5, default="NA", choices=homerooms)
    grade = models.IntegerField(default=-1)
    bday = models.DateField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    email = models.TextField(null=True, blank=True)
    canvas_id = models.IntegerField(null=True, blank=True)
    used_stars = models.IntegerField(null=False, blank=False, default=0)

    def is_sixth(self):
        return "6" in self.homeroom

    def name(self):
        return f"{self.fname} {self.lname}"

    def last_initial(self):
        if self.grade > 12: return self.lname

        names = re.split("[, ]", self.lname)
        first_letters = [a[0] for a in names]
        return "".join(first_letters)

    def short_section(self):
        if self.grade != 6: return self.get_homeroom_display()

        return self.get_homeroom_display()[2:]

    def get_total_stars(self):
        subs = self.submission_set.all()
        stars = 0
        for sub in subs:
            if sub.satisfactory != False:
                stars += sub.assignment.name.count("⭐")
                stars += sub.assignment.name.count("✴")

        return stars

    def get_remaining_stars(self):
        return self.get_total_stars() - self.used_stars

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.id}, {self.homeroom})"

    def __bool__(self):
        return self.enabled


class Assignment(models.Model):
    canvas_id = models.BigIntegerField(unique=True, primary_key=True)
    name = models.TextField()
    module = models.TextField()

    def __str__(self):
        return self.name


class Submission(models.Model):
    canvas_id = models.BigIntegerField(unique=True, primary_key=True)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    assignment = models.ForeignKey("Assignment", on_delete=models.CASCADE)
    satisfactory = models.BooleanField(null=True)
    submitted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{str(self.student)} submitted {str(self.assignment)}"


class TeambuildingQuestion(models.Model):
    text = models.TextField()
    active = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    grade = models.IntegerField(default=6)
    answer_list = models.TextField()  # Serialized as a JSON array of strings

    def set_answers(self, ans_list):
        self.answer_list = json.dumps(ans_list)

    def get_answers(self):
        if self.answer_list:
            return json.loads(self.answer_list)
        else:
            return []

    def __str__(self):
        return f"({self.grade}) {self.text} ({', '.join(self.get_answers())})"


class TeambuildingResponse(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    question = models.ForeignKey("TeambuildingQuestion", on_delete=models.CASCADE, related_name="response")
    answer = models.TextField()

    def __str__(self):
        return f"{self.student.fname} {self.student.lname} answered \"{self.answer}\" to \"{self.question.text}\""


class EntryTicket(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    seating_location = models.TextField()
    objective = models.ForeignKey("Assignment", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"EntryTicket {self.date} from {str(self.student)}"


class ExitTicket(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    learning_goal = models.TextField(null=True, blank=True)
    understanding = models.IntegerField(default=5)
    extra = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"ExitTicket {self.date} from {str(self.student)}"

    def __int__(self):
        return self.understanding


class MusicSuggestion(models.Model):
    song = models.TextField(null=False, blank=False)
    artist = models.TextField(null=True, blank=True)
    student = models.ForeignKey("Student", default="dc74089", on_delete=models.SET_DEFAULT)
    for_playlist = models.BooleanField()
    investigated = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.artist:
            return f"{str(self.student)} suggested {self.song} by {self.artist}{'*' if not self.investigated else ''}"
        else:
            return f"{str(self.student)} suggested {self.song}{'*' if not self.investigated else ''}"


class SiteConfig(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.BooleanField(default=False)

    def __str__(self):
        return self.key

    def __bool__(self):
        return self.value

    @staticmethod
    def init():
        SiteConfig.objects.get_or_create(key="student_login")
        SiteConfig.objects.get_or_create(key="entry_ticket")
        SiteConfig.objects.get_or_create(key="covid")
        SiteConfig.objects.get_or_create(key="exit_ticket_understanding")
        SiteConfig.objects.get_or_create(key="exit_ticket_extra")
        SiteConfig.objects.get_or_create(key="answer_questions")
        SiteConfig.objects.get_or_create(key="music")

    @staticmethod
    def all_configs():
        return {s.key: s.value for s in SiteConfig.objects.all()}
