from django.contrib import admin
from .models import (
    Post, Comment, Contact,
    Service, ContactSidebar,
    FAQ, SystemPrompt,
    AboutSection
)

from django_q.models import Schedule
from django_q.admin import ScheduleAdmin
from django.contrib.admin.sites import AlreadyRegistered


# Custom admin for AboutSection
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    ordering = ['order']

# Register your models
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Service)
admin.site.register(ContactSidebar)
admin.site.register(FAQ)
admin.site.register(SystemPrompt)
admin.site.register(AboutSection, AboutSectionAdmin)

# Safe registration for Django Q Schedule model
try:
    admin.site.unregister(Schedule)  # Avoid AlreadyRegistered error
except admin.sites.NotRegistered:
    pass

try:
    admin.site.register(Schedule, ScheduleAdmin)
except AlreadyRegistered:
    pass

# Custom admin site headers
admin.site.site_header = 'TherapyPoint | ADMIN PANEL'
admin.site.site_title = 'TherapyPoint | Admin'
admin.site.index_title = 'TherapyPoint Site Administration'
