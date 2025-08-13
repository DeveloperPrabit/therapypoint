from django.contrib import admin
from django import forms
from django.db.models.functions import TruncDate
from django.db.models import Count
import json
from .models import (
    Footer, TherapyMethod, TherapySubMethod, Post, Comment, Contact,
    Service, ContactSidebar, FAQ, SystemPrompt, AboutSection, AboutImage,
    Video, BlogMedia, Visitor, CarouselSlide, CarouselImage, AdditionalContent,
    FundingOption, FundingOptionImage, FundingOptionPage, FundingDetail,
    AppointmentRequest,
)

class TherapySubMethodInline(admin.TabularInline):
    model = TherapySubMethod
    extra = 0

@admin.register(TherapyMethod)
class TherapyMethodAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)
    inlines = [TherapySubMethodInline]

    def save_model(self, request, obj, form, change):
        if not obj.title:
            raise ValidationError("A title is required for this therapy method.")
        super().save_model(request, obj, form, change)

@admin.register(TherapySubMethod)
class TherapySubMethodAdmin(admin.ModelAdmin):
    list_display = ('therapy', 'name')
    list_filter = ('therapy',)

class FundingDetailInline(admin.TabularInline):
    model = FundingDetail
    extra = 0

@admin.register(FundingOptionPage)
class FundingOptionPageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    inlines = [FundingDetailInline]

class AboutImageInline(admin.TabularInline):
    model = AboutImage
    extra = 1
    fields = ['image', 'alignment', 'order']

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    ordering = ['order']
    inlines = [AboutImageInline]

class CarouselImageInline(admin.TabularInline):
    model = CarouselImage
    extra = 3
    fields = ['image', 'link', 'order']

class FundingOptionImageInline(admin.TabularInline):
    model = FundingOptionImage
    extra = 3
    fields = ['image', 'order']

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']
    inlines = [CarouselImageInline]

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ['slide', 'order', 'image']
    list_filter = ['slide']
    search_fields = ['slide__title']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_file', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(BlogMedia)
class BlogMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_file', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(Visitor)
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

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'copyright_text']
    fieldsets = (
        ("General Info", {
            'fields': ('organization_name', 'logo', 'tagline')
        }),
        ("Social Media Links", {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok')
        }),
        ("About Section", {
            'fields': ('about_heading', 'about_links')
        }),
        ("Services Section", {
            'fields': ('services_heading',)
        }),
        ("Support Section", {
            'fields': ('support_heading', 'support_text', 'support_link', 'book_text', 'book_link')
        }),
        ("Bottom Section", {
            'fields': ('locations', 'copyright_text', 'bottom_links', 'designer_text', 'designer_link')
        }),
    )

@admin.register(AdditionalContent)
class AdditionalContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'link_url']
    search_fields = ['title']

@admin.register(FundingOption)
class FundingOptionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [FundingOptionImageInline]

@admin.register(FundingOptionImage)
class FundingOptionImageAdmin(admin.ModelAdmin):
    list_display = ['funding_option', 'order', 'image']
    list_filter = ['funding_option']
    search_fields = ['funding_option__name']

@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', "email", 'phone', 'preferred_time', 'created_at', 'processed')
    list_filter = ('processed', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    ordering = ('-created_at',)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Service)
admin.site.register(ContactSidebar)
admin.site.register(FAQ)
admin.site.register(SystemPrompt)

admin.site.site_header = 'TherapyPoint | ADMIN PANEL'
admin.site.site_title = 'TherapyPoint | Admin'
admin.site.index_title = 'TherapyPoint Site Administration'