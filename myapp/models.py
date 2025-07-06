from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

now =  datetime.now()
time = now.strftime("%d %B %Y")
# Create your models here.

# Models for the TherapyPoint homepage video
from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/', max_length=255)  # <- increased from 100 to 255
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Post(models.Model):
    postname = models.CharField(max_length=600)
    category = models.CharField(max_length=600)
    image = models.ImageField(upload_to='images/posts',blank=True,null=True)
    content = models.CharField(max_length=100000)
    time = models.CharField(default=time,max_length=100, blank=True)
    likes = models.IntegerField(null=True,blank=True,default=0)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return str( self.postname)
    
# Import CKEditor rich text field
# Make sure you have installed django-ckeditor in your Django project
from django_ckeditor_5.fields import CKEditor5Field  # ✅ CKEditor 5 import

class AboutSection(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)

    # ✅ Use CKEditor5Field instead of RichTextField
    content = CKEditor5Field('Content', config_name='default')

    image = models.ImageField(upload_to='about/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

# Model for blog media files
class BlogMedia(models.Model):
    title = models.CharField(max_length=255)
    media_file = models.FileField(upload_to='blog_media/', max_length=255)  # ⬅️ increase from default 100 to 255
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="images/services", blank=True, null=True)

    def __str__(self):
        return self.title


    
    
class Comment(models.Model):
    content = models.CharField(max_length=200)
    time = models.CharField(default=time,max_length=100, blank=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return  f"{self.id}.{self.content[:20]}..."
    
    

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

#chatbot model
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
# yourapp/models.py
from django.db import models

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    visited_at = models.DateTimeField(auto_now_add=True)
    is_organic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ip_address} - {'Organic' if self.is_organic else 'Inorganic'}"
