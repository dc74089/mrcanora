import json

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
    ("6A", "6A"),
    ("6B", "6B"),
    ("6C", "6C"),
    ("6D", "6D"),
    ("6E", "6E"),
    ("6F", "6F"),
    ("6G", "6G"),
    ("6H", "6H"),
    ("NA", "N/A"),
)


# Create your models here.
class Student(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    fname = models.TextField()
    lname = models.TextField()
    homeroom = models.CharField(max_length=5, default="NA", choices=homerooms)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.id}, {self.homeroom})"


class TeambuildingQuestion(models.Model):
    text = models.TextField()
    active = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    answer_list = models.TextField()  # Serialized as a JSON array of strings

    def set_answers(self, ans_list):
        self.answer_list = json.dumps(ans_list)

    def get_answers(self):
        if self.answer_list:
            return json.loads(self.answer_list)
        else:
            return []

    def __str__(self):
        return f"{self.text} ({', '.join(self.get_answers())})"


class TeambuildingResponse(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    question = models.ForeignKey("TeambuildingQuestion", on_delete=models.CASCADE, related_name="response")
    answer = models.TextField()

    def __str__(self):
        return f"{self.student.fname} {self.student.lname} answered \"{self.answer}\" to \"{self.question.text}\""


class ExitTicket(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    learning_goal = models.TextField()
    understanding = models.IntegerField()
    extra = models.TextField()

    def __str__(self):
        return f"ExitTicket {self.date} from {str(self.student)}"

    def __int__(self):
        return self.understanding


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
        SiteConfig.objects.get_or_create(key="exit_ticket")
        SiteConfig.objects.get_or_create(key="answer_questions")
        SiteConfig.objects.get_or_create(key="view_answers")
        SiteConfig.objects.get_or_create(key="escape")
