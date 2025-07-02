from django.contrib import admin
from django import forms
from django_ckeditor_5.fields import CKEditor5Field
from django_ckeditor_5.widgets import CKEditor5Widget  # ✅ Fix: Add this line

from .models import (
    Post, Comment, Contact,
    Service, ContactSidebar,
    FAQ, SystemPrompt,
    AboutSection, Video
)

from django_q.models import Schedule
from django_q.admin import ScheduleAdmin
from django.contrib.admin.sites import AlreadyRegistered

# ✅ CKEditor5-enabled form for AboutSection
class AboutSectionAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = AboutSection
        fields = '__all__'

# ✅ Admin customization for AboutSection
class AboutSectionAdmin(admin.ModelAdmin):
    form = AboutSectionAdminForm
    list_display = ['title', 'order']
    ordering = ['order']

# ✅ Video admin
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_file', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

# ✅ Register other models
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Service)
admin.site.register(ContactSidebar)
admin.site.register(FAQ)
admin.site.register(SystemPrompt)
admin.site.register(AboutSection, AboutSectionAdmin)

# ✅ Safe registration for Django Q Scheduler
try:
    admin.site.unregister(Schedule)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.register(Schedule, ScheduleAdmin)
except AlreadyRegistered:
    pass

# ✅ Admin branding
admin.site.site_header = 'TherapyPoint | ADMIN PANEL'
admin.site.site_title = 'TherapyPoint | Admin'
admin.site.index_title = 'TherapyPoint Site Administration'
