from django.urls import path

from .views import auth, views, questions, configuration

urlpatterns = [
    path('login/admin', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),

    path('login/student', views.student_login, name="student_login"),

    path('', views.index, name="index"),
    path('admin', views.admin, name="admin"),

    path('questions/create', questions.create, name="create_question"),
    path('questions/select', questions.select, name="choose_questions"),
    path('configuration/set', configuration.configure, name="configure"),
]
