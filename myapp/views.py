from django.shortcuts import render, redirect, get_object_or_404
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
import mimetypes

from .models import (
    Post, Comment, Service, ContactSidebar, Video, AboutSection,
    FAQ, SystemPrompt, CarouselSlide, AdditionalContent, FundingOption,
    TherapyMethod, AboutImage, BlogMedia, AppointmentRequest, FundingOptionPage,
    Footer
)

user_sessions = {}

def index(request):
    videos = Video.objects.all().order_by('-created_at')
    posts = Post.objects.filter(user_id=request.user.id).order_by("-id") if request.user.is_authenticated else []
    about_section = AboutSection.objects.order_by('order').first()
    services = Service.objects.all()[:2]
    carousel_slides = CarouselSlide.objects.filter(is_active=True).prefetch_related('images')
    additional_content = AdditionalContent.objects.all()
    funding_options = FundingOption.objects.all().prefetch_related('images')

    return render(request, "index.html", {
        'videos': videos,
        'posts': posts,
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        'about_section': about_section,
        'home_services': services,
        'carousel_slides': carousel_slides,
        'additional_content': additional_content,
        'funding_options': funding_options
    })

def about_us(request):
    sections = AboutSection.objects.all().order_by('order').prefetch_related('images')
    return render(request, 'about.html', {'sections': sections})

def home(request):
    carousel_slides = CarouselSlide.objects.filter(is_active=True).prefetch_related('images')
    return render(request, 'index.html', {
        'carousel_slides': carousel_slides,
    })

def services(request):
    services = Service.objects.all()[:6]
    return render(request, "services.html", {
        "services": services,
        "show_view_all": Service.objects.count() > 6
    })

def services_all(request):
    services = Service.objects.all()
    return render(request, "services_all.html", {
        "services": services
    })

def service_detail(request, id):
    service = Service.objects.get(id=id)
    return render(request, "service_detail.html", {
        "service": service,
        "media_url": settings.MEDIA_URL
    })

@login_required
def create_service(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to create services.")
        return redirect('services')
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES.get('image')
        Service.objects.create(title=title, description=description, image=image)
        messages.success(request, "Service created successfully.")
        return redirect('services')
    return render(request, "create_service.html")

@login_required
def edit_service(request, id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit services.")
        return redirect('services')
    service = Service.objects.get(id=id)
    if request.method == 'POST':
        service.title = request.POST['title']
        service.description = request.POST['description']
        if request.FILES.get('image'):
            service.image = request.FILES['image']
        service.save()
        messages.success(request, "Service updated successfully.")
        return redirect('services')
    return render(request, "edit_service.html", {'service': service})

@login_required
def delete_service(request, id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete services.")
        return redirect('services')
    Service.objects.get(id=id).delete()
    messages.success(request, "Service deleted successfully.")
    return redirect('services')

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
    media_files = BlogMedia.objects.all().order_by('-created_at')
    for media in media_files:
        file_path = media.media_file.path
        mime_type, _ = mimetypes.guess_type(file_path) or ('', '')
        media.is_video = mime_type.startswith("video/")

    return render(request, "blog.html circa 2006", {
        'media_files': media_files,
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

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def footer_view(request):
    footer = Footer.objects.last()
    therapy_methods = TherapyMethod.objects.order_by('order')
    return render(request, 'footer.html', {
        'footer': footer,
        'therapy_methods': therapy_methods,
    })

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

            AppointmentRequest.objects.create(
                full_name=session['name'],
                email=session['email'],
                phone=session['phone'],
                preferred_time=session['time'],
            )

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

            response = f"✅ Thank you, {session['name']}! Your appointment for {session['time']} has been received. We will contact you shortly."
            user_sessions.pop(session_id)
            return JsonResponse({'response': response})

        faq_match = FAQ.objects.filter(question__icontains=message).first()
        if faq_match:
            return JsonResponse({'response': faq_match.answer})

        system_prompt = SystemPrompt.objects.last()
        default_response = system_prompt.prompt_text if system_prompt else "Hi! You can say 'book an appointment' or ask a question."
        return JsonResponse({'response': default_response})

    return JsonResponse({'response': "❌ Invalid request method."})

def funding_option_view(request):
    funding = get_object_or_404(FundingOptionPage)
    return render(request, 'funding_option.html', {'funding': funding})

def therapy_methods_list(request):
    therapy_methods = TherapyMethod.objects.all()
    return render(request, 'therapymethods_list.html', {
        'therapy_methods': therapy_methods,
        'media_url': settings.MEDIA_URL
    })

def therapy_method_detail(request, pk):
    therapy = get_object_or_404(TherapyMethod, pk=pk)
    return render(request, 'therapymethods.html', {
        'therapy': therapy,
        'media_url': settings.MEDIA_URL
    })