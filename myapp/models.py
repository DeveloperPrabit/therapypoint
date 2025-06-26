from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

now =  datetime.now()
time = now.strftime("%d %B %Y")
# Create your models here.


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
