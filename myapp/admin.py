from django.contrib import admin
from .models import Post,Comment,Contact
from .models import Service  # Add this
from .models import ContactSidebar
from .models import FAQ, SystemPrompt
from .models import AboutSection



# Register your models here.
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    ordering = ['order']

admin.site.register(AboutSection, AboutSectionAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Service)
admin.site.register(FAQ)
admin.site.register(SystemPrompt)


admin.site.register(ContactSidebar)




admin.site.site_header = 'BLOGSPOT | ADMIN PANEL'
admin.site.site_title = 'BLOGSPOT | BLOGGING WEBSITE'
admin.site.index_title= 'BlogSpot Site Administration'
