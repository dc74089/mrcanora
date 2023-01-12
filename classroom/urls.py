from django.urls import path, re_path
from django.views.static import serve

from mrcanora import settings
from .views import auth, views, questions, configuration, entryticket, exitticket, students, sixth, music, ai

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
    path('music/public/view/please/dont/share', music.view_music_helper, name="music_public"),

    path('configuration/set', configuration.configure, name="configure"),

    path('sixth/tracker/<str:group>', sixth.tracker, name="sixth_tracker"),
    path('sixth/stars/spend', sixth.spend_stars, name="sixth_spend_stars"),

    path('ai/studio', ai.ai_index, name="ai"),
    path('ai/studio/submit', ai.new_request, name="ai_submit"),
    path('ai/studio/cancel/<str:id>', ai.cancel, name="ai_cancel"),

    path('ai/train', ai.training, name="ai_training"),

    path('ai/moderate', ai.moderate, name="ai_moderate"),
    path('ai/queue', ai.ai_queue, name="ai_queue"),
    path('ai/exemplars', ai.exemplars, name="ai_exemplars"),

    path('ai/api/getnext', ai.api_get_next_job, name="ai_api_nextjob"),
    path('ai/api/markcurrent', ai.api_mark_in_progress, name="ai_api_markinprogress"),
    path('ai/api/submitimage', ai.api_submit_image, name="ai_api_submitimage"),
]


if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
