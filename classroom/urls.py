from django.urls import path

from .views import auth, views, questions, configuration, entryticket, exitticket, students, sixth, music

urlpatterns = [
    path('login/admin', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),

    path('login/student', views.student_login, name="student_login"),

    path('', views.index, name="index"),
    path('admin', views.admin, name="admin"),
    path('admin/rosters', students.rosters, name="rosters"),
    path('admin/import_students', students.import_students, name="import_students"),
    path('admin/import_bday', students.import_bdays, name="import_bdays"),
    path('admin/activate', students.activate_homeroom, name="activate_homeroom"),
    path('admin/rollover', students.rollover, name="rollover"),

    path('questions/create', questions.create, name="create_question"),
    path('questions/select', questions.select, name="choose_questions"),
    path('questions/answer', questions.answer, name="answer_question"),
    path('questions/view', questions.view, name="view_answers"),

    path('exitticket/submit', exitticket.submit, name="submit_exitticket"),
    path('exitticket/analytics', exitticket.view, name="view_analytics"),

    path('entryticket/submit', entryticket.submit, name="submit_entryticket"),
    path('entryticket/status', entryticket.entryticket_status, name="entryticket_status"),
    path('contacttrace', entryticket.contact_trace, name="contacttrace"),

    path('music/submit', music.submit_music, name="music_submit"),
    path('music/dismiss/<int:id>', music.dismiss, name="music_dismiss"),
    path('music/dismiss', music.hide_for_student, name="music_dismiss_student"),
    path('music', music.view_music, name="music"),

    path('configuration/set', configuration.configure, name="configure"),

    path('sixth/tracker/<str:group>', sixth.tracker, name="sixth_tracker"),
    path('sixth/stars/spend', sixth.spend_stars, name="sixth_spend_stars"),
]
