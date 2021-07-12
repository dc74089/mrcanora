from django.urls import path

from .views import auth, views, questions, configuration, exitticket, students, sixth

urlpatterns = [
    path('login/admin', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),

    path('login/student', views.student_login, name="student_login"),

    path('', views.index, name="index"),
    path('admin', views.admin, name="admin"),

    path('admin/import_students', students.import_students, name="import_students"),

    path('questions/create', questions.create, name="create_question"),
    path('questions/select', questions.select, name="choose_questions"),
    path('questions/answer', questions.answer, name="answer_question"),
    path('questions/view', questions.view, name="view_answers"),

    path('exitticket/submit', exitticket.submit, name="submit_exitticket"),
    path('exitticket/analytics', exitticket.view, name="view_analytics"),

    path('configuration/set', configuration.configure, name="configure"),

    path('escape', views.escape, name="escape"),

    path('sixth/tracker/<str:group>', sixth.tracker, name="sixth_tracker"),
]
