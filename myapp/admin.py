from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from django.db.models.functions import TruncDate
from django.db.models import Count
import json

from .models import (
    Post, Comment, Contact,
    Service, ContactSidebar,
    FAQ, SystemPrompt,
    AboutSection, Video,
    BlogMedia, Visitor  # ✅ Make sure Visitor is included
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

# ✅ Video Admin
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_file', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

# ✅ Blog Media Admin
@admin.register(BlogMedia)
class BlogMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_file', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

# ✅ Visitor Admin with chart
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'visited_at', 'is_organic', 'short_user_agent')
    list_filter = ('is_organic', 'visited_at')
    search_fields = ('ip_address', 'user_agent')
    change_list_template = 'admin/visitor_stats.html'

    def short_user_agent(self, obj):
        return (obj.user_agent[:60] + '...') if len(obj.user_agent) > 60 else obj.user_agent
    short_user_agent.short_description = 'User Agent'

    def changelist_view(self, request, extra_context=None):
        total = Visitor.objects.count()
        organic = Visitor.objects.filter(is_organic=True).count()
        inorganic = total - organic

        recent_visitors = (
            Visitor.objects.annotate(date=TruncDate('visited_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        chart_labels = [str(entry['date']) for entry in recent_visitors]
        chart_data = [entry['count'] for entry in recent_visitors]

        extra_context = extra_context or {}
        extra_context.update({
            'total_visitors': total,
            'organic': organic,
            'inorganic': inorganic,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        })
        return super().changelist_view(request, extra_context=extra_context)

# ✅ Register everything else
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Service)
admin.site.register(ContactSidebar)
admin.site.register(FAQ)
admin.site.register(SystemPrompt)
admin.site.register(AboutSection, AboutSectionAdmin)
admin.site.register(Visitor, VisitorAdmin)  # ✅ This was missing

# ✅ Safe registration of Django Q scheduler
try:
    admin.site.unregister(Schedule)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.register(Schedule, ScheduleAdmin)
except AlreadyRegistered:
    pass

# ✅ Admin site branding
admin.site.site_header = 'TherapyPoint | ADMIN PANEL'
admin.site.site_title = 'TherapyPoint | Admin'
admin.site.index_title = 'TherapyPoint Site Administration'
