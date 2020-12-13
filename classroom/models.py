import json

from django.db import models


# Create your models here.
class Student(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    fname = models.TextField()
    lname = models.TextField()
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.id})"


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
    question = models.ForeignKey("TeambuildingQuestion", on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return f"{self.student.fname} {self.student.lname} answered \"{self.answer}\" to \"{self.question.text}\""
