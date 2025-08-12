from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

now = datetime.now()
time = now.strftime("%d %B %Y")

# Create your models here.
from django.db import models

class CarouselSlide(models.Model):
    title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Carousel Slide {self.id}"

class CarouselImage(models.Model):
    slide = models.ForeignKey(CarouselSlide, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='carousel/')
    link = models.URLField(blank=True, help_text="Optional: Add link to image (if any)")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image {self.order} for {self.slide.title}"

# Models for the TherapyPoint homepage video
class Video(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    postname = models.CharField(max_length=600)
    category = models.CharField(max_length=600)
    image = models.ImageField(upload_to='images/posts', blank=True, null=True)
    content = models.CharField(max_length=100000)
    time = models.CharField(default=time, max_length=100, blank=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.postname)

from django_ckeditor_5.fields import CKEditor5Field

class AboutSection(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    content = CKEditor5Field('Content', config_name='default')
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class BlogMedia(models.Model):
    title = models.CharField(max_length=255)
    media_file = models.FileField(upload_to='blog_media/', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ServiceManager(models.Manager):
    def delete_service(self, id):
        service = self.get(id=id)
        service.delete()
        services = self.filter(id__gt=id).order_by('id')
        for service in services:
            service.id -= 1
            service.save()

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="images/services", blank=True, null=True)
    objects = ServiceManager()

    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.CharField(max_length=200)
    time = models.CharField(default=time, max_length=100, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.id}.{self.content[:20]}..."

class Contact(models.Model):
    name = models.CharField(max_length=600)
    email = models.EmailField(max_length=600)
    subject = models.CharField(max_length=1000)
    message = models.CharField(max_length=10000, blank=True)

class ContactSidebar(models.Model):
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    office1_label = models.CharField(max_length=100)
    office1_address = models.TextField()
    office2_label = models.CharField(max_length=100)
    office2_address = models.TextField()
    hours_weekdays = models.CharField(max_length=100)
    hours_saturday = models.CharField(max_length=100)
    hours_sunday = models.CharField(max_length=100)

    def __str__(self):
        return "Contact Sidebar Info"

#chatbot models

class AppointmentRequest(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    preferred_time = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)  # mark handled or not

    def __str__(self):
        return f"{self.full_name} - {self.preferred_time}"

# This model is for the footer content

class Footer(models.Model):
    organization_name = models.CharField(max_length=255, default="Activ Therapy")
    logo = models.ImageField(upload_to='footer/', blank=True, null=True)
    tagline = models.CharField(max_length=255, default="Live Healthier and Happier for Longer")
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    about_heading = models.CharField(max_length=100, default="Activ Therapy")
    about_links = models.TextField(blank=True, help_text="Format: Label|URL (one per line)")
    services_heading = models.CharField(max_length=100, default="Services")
    support_heading = models.CharField(max_length=100, default="Support")
    support_text = models.CharField(max_length=255, default="(02) 9726 4491")
    support_link = models.URLField(default="tel:0297264491")
    book_text = models.CharField(max_length=255, default="Book Now")
    book_link = models.URLField(default="#")
    locations = models.TextField(blank=True, help_text="Format: Label|URL (one per line)")
    copyright_text = models.CharField(max_length=255, default="Copyright ©2024 Activ Therapy")
    bottom_links = models.TextField(blank=True, help_text="Format: Label|URL (one per line)")
    designer_text = models.CharField(max_length=255, default="Locally - Local Experts")
    designer_link = models.URLField(default="#")

    def get_about_links(self):
        return [line.split('|') for line in self.about_links.strip().splitlines() if '|' in line]

    def get_locations(self):
        return [line.split('|') for line in self.locations.strip().splitlines() if '|' in line]

    def get_bottom_links(self):
        return [line.split('|') for line in self.bottom_links.strip().splitlines() if '|' in line]

    def __str__(self):
        return f"Footer for {self.organization_name}"



class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    def __str__(self):
        return self.question

class SystemPrompt(models.Model):
    prompt_text = models.TextField(help_text="Custom system instruction for the chatbot.")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "System Prompt"

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    visited_at = models.DateTimeField(auto_now_add=True)
    is_organic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ip_address} - {'Organic' if self.is_organic else 'Inorganic'}"

class AdditionalContent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link_url = models.URLField()

    def __str__(self):
        return self.title

class FundingOption(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class FundingOptionImage(models.Model):
    funding_option = models.ForeignKey(FundingOption, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='funding/')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image {self.order} for {self.funding_option.name}"

class CustomCode(models.Model):
    css_code = models.TextField(blank=True, null=True)
    js_code = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Custom Code ({self.updated_at.strftime('%Y-%m-%d %H:%M')})"


from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

class FundingOptionPage(models.Model):
    title = models.CharField(max_length=200)
    intro_text = CKEditor5Field('Intro Text', config_name='default', blank=True)
    extra_info = CKEditor5Field('Extra Info', config_name='default', blank=True)
    image = models.ImageField(upload_to='funding_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class FundingDetail(models.Model):
    funding_option = models.ForeignKey(FundingOptionPage, related_name='details', on_delete=models.CASCADE)
    heading = models.CharField(max_length=200)
    description = CKEditor5Field('Description', config_name='default')

    def __str__(self):
        return self.heading
    
    #This model for therapy methods and sub-methods


class TherapyMethod(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='therapy_methods/', blank=True, null=True)  # Make image optional
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title



class TherapySubMethod(models.Model):
    therapy = models.ForeignKey(TherapyMethod, related_name='methods', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.therapy.title} - {self.name}"