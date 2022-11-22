from django.contrib import admin
from .models import *


class ExitTicketAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)


# Register your models here.
admin.site.register(Student)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(TeambuildingQuestion)
admin.site.register(TeambuildingResponse)
admin.site.register(SiteConfig)
admin.site.register(MusicSuggestion)
admin.site.register(EntryTicket, ExitTicketAdmin)
admin.site.register(ExitTicket, ExitTicketAdmin)
admin.site.register(ArtRequest)
