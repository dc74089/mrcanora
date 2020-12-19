from django.contrib import admin
from .models import *


class ExitTicketAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)


# Register your models here.
admin.site.register(Student)
admin.site.register(TeambuildingQuestion)
admin.site.register(TeambuildingResponse)
admin.site.register(SiteConfig)
admin.site.register(ExitTicket, ExitTicketAdmin)
