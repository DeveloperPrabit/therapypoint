from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django_q.tasks import schedule
import json

from .models import (
    Post, Comment, Service, ContactSidebar,
    Video, AboutSection, FAQ, SystemPrompt
)
from .tasks import place_missed_call

user_sessions = {}

# ✅ Homepage View
def index(request):
    videos = Video.objects.all().order_by('-created_at')
    posts = Post.objects.filter(user_id=request.user.id).order_by("-id") if request.user.is_authenticated else []
    about_section = AboutSection.objects.order_by('order').first()
    services = Service.objects.all()[:2]  # Limit to 2 services for homepage

    return render(request, "index.html", {
        'videos': videos,
        'posts': posts,
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        'about_section': about_section,
        'home_services': services
    })

# ✅ About Page
def about_us(request):
    sections = AboutSection.objects.all().order_by('order')
    return render(request, 'about.html', {'sections': sections})

# ✅ Services Page
def services(request):
    services = Service.objects.all()
    return render(request, "services.html", {"services": services})

# ✅ Signup
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

# ✅ Signin
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

# ✅ Logout
def logout(request):
    auth.logout(request)
    return redirect('index')

# ✅ Blog View
def blog(request):
    return render(request, "blog.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("-id"),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })

# ✅ Create Post
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

# ✅ Profile View
def profile(request, id):
    return render(request, 'profile.html', {
        'user': User.objects.get(id=id),
        'posts': Post.objects.all(),
        'media_url': settings.MEDIA_URL,
    })

# ✅ Profile Edit
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

# ✅ Increase Likes
def increaselikes(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save()
    return redirect("index")

# ✅ Single Post Details
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

# ✅ Save Comment
def savecomment(request, id):
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id=id, user_id=request.user.id, content=content).save()
    return redirect("index")

# ✅ Delete Comment
def deletecomment(request, id):
    comment = Comment.objects.get(id=id)
    post_id = comment.post.id
    comment.delete()
    return post(request, post_id)

# ✅ Edit Post
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

# ✅ Delete Post
def deletepost(request, id):
    Post.objects.get(id=id).delete()
    return profile(request, request.user.id)

# ✅ Contact Us Page + Email Sending
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

# ✅ Chatbot API View
@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = request.session.session_key or request.session.save()

        if session_id not in user_sessions:
            user_sessions[session_id] = {'step': None}

        session = user_sessions[session_id]

        if "appointment" in message.lower() and session['step'] is None:
            session['step'] = 'name'
            return JsonResponse({'response': "Sure! Let's book your appointment. What's your full name?"})

        if session['step'] == 'name':
            session['name'] = message.title()
            session['step'] = 'email'
            return JsonResponse({'response': f"Thanks {session['name']}! What's your email address?"})

        if session['step'] == 'email':
            session['email'] = message
            session['step'] = 'phone'
            return JsonResponse({'response': "Got it. What's your phone number?"})

        if session['step'] == 'phone':
            session['phone'] = message
            session['step'] = 'time'

            time_options = ['10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM']
            buttons = "".join([
                f"<button onclick=\"sendMessage('{t}')\" class='btn btn-outline-primary btn-sm m-1'>{t}</button>"
                for t in time_options
            ])
            return JsonResponse({'response': "Choose your preferred time:<br>" + buttons})

        if session['step'] == 'time':
            session['time'] = message
            session['step'] = 'done'

            subject = "New Appointment Request"
            body = f"""
New Appointment Request:

Name: {session['name']}
Email: {session['email']}
Phone: {session['phone']}
Preferred Time: {session['time']}
"""
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                ['prabitjoshi@gmail.com'],
                fail_silently=False
            )

            try:
                appointment_time = datetime.strptime(session['time'], '%I %p')
                now = datetime.now()
                appointment_datetime = datetime.combine(now.date(), appointment_time.time())
                aware_appointment = make_aware(appointment_datetime)
                phone_number = '+977' + session['phone'].lstrip('0')

                schedule('myapp.tasks.place_missed_call', phone_number, hook='myapp.tasks.log_result',
                         next_run=aware_appointment - timedelta(hours=1),
                         task_name=f"Reminder for {session['name']}")
                schedule('myapp.tasks.place_missed_call', phone_number, hook='myapp.tasks.log_result',
                         next_run=aware_appointment - timedelta(minutes=30),
                         task_name=f"Missed Call for {session['name']}")
                schedule('myapp.tasks.place_missed_call', phone_number, hook='myapp.tasks.log_result',
                         next_run=aware_appointment + timedelta(minutes=10),
                         task_name=f"Follow-up Call for {session['name']}")
            except Exception as e:
                print("❌ Scheduling failed:", e)

            response = f"✅ Thank you, {session['name']}! Your appointment for {session['time']} has been received."
            user_sessions.pop(session_id)
            return JsonResponse({'response': response})

        faq_match = FAQ.objects.filter(question__icontains=message).first()
        if faq_match:
            return JsonResponse({'response': faq_match.answer})

        system_prompt = SystemPrompt.objects.last()
        default_response = system_prompt.prompt_text if system_prompt else "Hi! You can say 'book an appointment' or ask a question."
        return JsonResponse({'response': default_response})

    return JsonResponse({'response': "❌ Invalid request method."})
