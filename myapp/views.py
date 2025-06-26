from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import Post, Comment, Service, ContactSidebar


def index(request):
    return render(request, "index.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("-id"),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def services(request):
    services = Service.objects.all()
    return render(request, "services.html", {"services": services})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists")
            else:
                User.objects.create_user(username=username, email=email, password=password)
                return redirect('signin')
        else:
            messages.info(request, "Passwords do not match")
        return redirect('signup')
    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, 'Invalid credentials')
            return redirect("signin")
    return render(request, "signin.html")


def logout(request):
    auth.logout(request)
    return redirect('index')


def blog(request):
    return render(request, "blog.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("-id"),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def create(request):
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category = request.POST['category']
            image = request.FILES['image']
            Post(postname=postname, content=content, category=category, image=image, user=request.user).save()
        except:
            print("Error creating post")
        return redirect('index')
    return render(request, "create.html")


def profile(request, id):
    return render(request, 'profile.html', {
        'user': User.objects.get(id=id),
        'posts': Post.objects.all(),
        'media_url': settings.MEDIA_URL,
    })


def profileedit(request, id):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']

        user = User.objects.get(id=id)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.save()
        return profile(request, id)
    return render(request, "profileedit.html", {
        'user': User.objects.get(id=id),
    })


def increaselikes(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save()
    return redirect("index")


def post(request, id):
    post = Post.objects.get(id=id)
    comments = Comment.objects.filter(post_id=post.id)
    return render(request, "post-details.html", {
        "user": request.user,
        'post': post,
        'recent_posts': Post.objects.all().order_by("-id"),
        'media_url': settings.MEDIA_URL,
        'comments': comments,
        'total_comments': len(comments)
    })


def savecomment(request, id):
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id=id, user_id=request.user.id, content=content).save()
    return redirect("index")


def deletecomment(request, id):
    comment = Comment.objects.get(id=id)
    post_id = comment.post.id
    comment.delete()
    return post(request, post_id)


def editpost(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        try:
            post.postname = request.POST['postname']
            post.content = request.POST['content']
            post.category = request.POST['category']
            post.save()
        except:
            print("Error editing post")
        return profile(request, request.user.id)
    return render(request, "postedit.html", {'post': post})


def deletepost(request, id):
    Post.objects.get(id=id).delete()
    return profile(request, request.user.id)


def contact_us(request):
    context = {}
    sidebar = ContactSidebar.objects.first()
    context['sidebar'] = sidebar

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        service = request.POST.get('service')
        message = request.POST.get('message')
        locations = request.POST.getlist('location')

        subject = f"New Contact Form Submission - {service}"
        html_body = render_to_string('email/contact_email.html', {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'service': service,
            'message': message,
            'locations': locations,
        })

        try:
            email_msg = EmailMessage(
                subject=subject,
                body=html_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['prabitjoshi@gmail.com'],
                headers={'Reply-To': email}
            )
            email_msg.content_subtype = "html"
            email_msg.send()
            context['message'] = f"Thank you {name}, your message has been sent."
        except Exception as e:
            context['message'] = f"Oops! Something went wrong: {str(e)}"

    return render(request, "contact.html", context)
