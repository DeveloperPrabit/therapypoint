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
from django.core.exceptions import ValidationError

from .models import (
    Post, Comment, Service, ContactSidebar,
    Video, AboutSection, FAQ, SystemPrompt,
    CarouselSlide, AdditionalContent, FundingOption,
    BlogMedia, Footer, FundingOptionPage, TherapyMethod, AppointmentRequest
)

# Store user sessions for chatbot (consider using Django sessions instead for persistence)
user_sessions = {}

# Homepage View
def index(request):
    videos = Video.objects.all().order_by('-created_at')
    posts = Post.objects.filter(user_id=request.user.id).order_by("-id") if request.user.is_authenticated else []
    about_section = AboutSection.objects.order_by('order').first()
    services = Service.objects.all()[:2]  # Limit to 2 services for homepage
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

# About Page
def about_us(request):
    sections = AboutSection.objects.all().order_by('order')
    return render(request, 'about.html', {'sections': sections})

# Home View (consider merging with index if functionality is similar)
def home(request):
    carousel_slides = CarouselSlide.objects.filter(is_active=True).prefetch_related('images')
    return render(request, 'index.html', {
        'carousel_slides': carousel_slides,
    })

# Services Page
def services(request):
    services = Service.objects.all()[:6]  # Limit to 6 services for display
    return render(request, "services.html", {
        "services": services,
        "show_view_all": Service.objects.count() > 6
    })

# All Services Page
def services_all(request):
    services = Service.objects.all()
    return render(request, "services_all.html", {
        "services": services
    })

# Service Detail View
def service_detail(request, id):
    service = get_object_or_404(Service, id=id)
    return render(request, "service_detail.html", {
        "service": service,
        "media_url": settings.MEDIA_URL
    })

# Create Service (Admin Only)
@login_required
def create_service(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to create services.")
        return redirect('services')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        if not title or not description:
            messages.error(request, "Title and description are required.")
            return render(request, "create_service.html")
        try:
            Service.objects.create(title=title, description=description, image=image)
            messages.success(request, "Service created successfully.")
            return redirect('services')
        except ValidationError as e:
            messages.error(request, f"Error creating service: {str(e)}")
    return render(request, "create_service.html")

# Edit Service (Admin Only)
@login_required
def edit_service(request, id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit services.")
        return redirect('services')
    service = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        service.title = request.POST.get('title')
        service.description = request.POST.get('description')
        if not service.title or not service.description:
            messages.error(request, "Title and description are required.")
            return render(request, "edit_service.html", {'service': service})
        if request.FILES.get('image'):
            service.image = request.FILES['image']
        try:
            service.save()
            messages.success(request, "Service updated successfully.")
            return redirect('services')
        except ValidationError as e:
            messages.error(request, f"Error updating service: {str(e)}")
    return render(request, "edit_service.html", {'service': service})

# Delete Service (Admin Only)
@login_required
def delete_service(request, id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete services.")
        return redirect('services')
    service = get_object_or_404(Service, id=id)
    service.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect('services')

# Signup
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not all([username, email, password, password2]):
            messages.error(request, "All fields are required.")
            return redirect('signup')
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
            else:
                User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, "Account created successfully. Please sign in.")
                return redirect('signin')
        else:
            messages.error(request, "Passwords do not match.")
        return redirect('signup')
    return render(request, "signup.html")

# Signin
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.error(request, 'Invalid credentials.')
            return redirect("signin")
    return render(request, "signin.html")

# Logout
def logout(request):
    auth.logout(request)
    return redirect('index')

# Blog View
def blog(request):
    media_files = BlogMedia.objects.all().order_by('-created_at')
    for media in media_files:
        file_path = media.media_file.path
        mime_type, _ = mimetypes.guess_type(file_path) or ('', '')
        media.is_video = mime_type.startswith("video/")

    return render(request, "blog.html", {
        'media_files': media_files,
        'posts': Post.objects.filter(user_id=request.user.id).order_by("-id") if request.user.is_authenticated else [],
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })

# Create Post
@login_required
def create(request):
    if request.method == 'POST':
        try:
            postname = request.POST.get('postname')
            content = request.POST.get('content')
            category = request.POST.get('category')
            image = request.FILES.get('image')
            if not all([postname, content, category, image]):
                messages.error(request, "All fields are required.")
                return render(request, "create.html")
            Post.objects.create(postname=postname, content=content, category=category, image=image, user=request.user)
            messages.success(request, "Post created successfully.")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Error creating post: {str(e)}")
    return render(request, "create.html")

# Profile View
def profile(request, id):
    user = get_object_or_404(User, id=id)
    return render(request, 'profile.html', {
        'user': user,
        'posts': Post.objects.filter(user_id=id),  # Show only user's posts
        'media_url': settings.MEDIA_URL,
    })

# Profile Edit
@login_required
def profileedit(request, id):
    user = get_object_or_404(User, id=id)
    if request.user.id != id:
        messages.error(request, "You can only edit your own profile.")
        return redirect('profile', id=id)
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        if not all([firstname, lastname, email]):
            messages.error(request, "All fields are required.")
            return render(request, "profileedit.html", {'user': user})
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        try:
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile', id=id)
        except ValidationError as e:
            messages.error(request, f"Error updating profile: {str(e)}")
    return render(request, "profileedit.html", {'user': user})

# Increase Likes
@login_required
def increaselikes(request, id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=id)
        post.likes += 1
        post.save()
        messages.success(request, "Like added.")
    return redirect("index")

# Single Post Details
def post(request, id):
    post = get_object_or_404(Post, id=id)
    comments = Comment.objects.filter(post_id=post.id)
    return render(request, "post-details.html", {
        "user": request.user,
        'post': post,
        'recent_posts': Post.objects.all().order_by("-id"),
        'media_url': settings.MEDIA_URL,
        'comments': comments,
        'total_comments': len(comments)
    })

# Save Comment
@login_required
def savecomment(request, id):
    if request.method == 'POST':
        content = request.POST.get('message')
        if not content:
            messages.error(request, "Comment cannot be empty.")
            return redirect('post', id=id)
        Comment.objects.create(post_id=id, user_id=request.user.id, content=content)
        messages.success(request, "Comment added successfully.")
    return redirect('post', id=id)

# Delete Comment
@login_required
def deletecomment(request, id):
    comment = get_object_or_404(Comment, id=id)
    post_id = comment.post.id
    if comment.user_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You can only delete your own comments.")
        return redirect('post', id=post_id)
    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect('post', id=post_id)

# Edit Post
@login_required
def editpost(request, id):
    post = get_object_or_404(Post, id=id)
    if post.user_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You can only edit your own posts.")
        return redirect('profile', id=request.user.id)
    if request.method == 'POST':
        try:
            post.postname = request.POST.get('postname')
            post.content = request.POST.get('content')
            post.category = request.POST.get('category')
            if not all([post.postname, post.content, post.category]):
                messages.error(request, "All fields are required.")
                return render(request, "postedit.html", {'post': post})
            post.save()
            messages.success(request, "Post updated successfully.")
            return redirect('profile', id=request.user.id)
        except Exception as e:
            messages.error(request, f"Error editing post: {str(e)}")
    return render(request, "postedit.html", {'post': post})

# Delete Post
@login_required
def deletepost(request, id):
    post = get_object_or_404(Post, id=id)
    if post.user_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You can only delete your own posts.")
        return redirect('profile', id=request.user.id)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('profile', id=request.user.id)

# Contact Us Page + Email Sending
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

        if not all([name, email, service, message]):
            context['message'] = "Please fill in all required fields."
            return render(request, "contact.html", context)

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

# Custom 404 View
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# Footer View
def footer_view(request):
    footer = Footer.objects.last()
    therapy_methods = TherapyMethod.objects.order_by('order')
    return render(request, 'footer.html', {
        'footer': footer,
        'therapy_methods': therapy_methods,
    })

# Chatbot API
@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = request.session.session_key or request.session.save()

            # Use Django session instead of in-memory dict for persistence
            if 'chatbot_step' not in request.session:
                request.session['chatbot_step'] = None
                request.session['chatbot_data'] = {}

            session = request.session['chatbot_data']
            step = request.session['chatbot_step']

            if "appointment" in message.lower() and step is None:
                request.session['chatbot_step'] = 'name'
                request.session.modified = True
                return JsonResponse({'response': "Sure! Let's book your appointment. What's your full name?"})

            if step == 'name':
                session['name'] = message.title()
                request.session['chatbot_step'] = 'email'
                request.session.modified = True
                return JsonResponse({'response': f"Thanks {session['name']}! What's your email address?"})

            if step == 'email':
                session['email'] = message
                request.session['chatbot_step'] = 'phone'
                request.session.modified = True
                return JsonResponse({'response': "Got it. What's your phone number?"})

            if step == 'phone':
                session['phone'] = message
                request.session['chatbot_step'] = 'time'
                request.session.modified = True
                time_options = ['10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM']
                buttons = "".join([
                    f"<button onclick=\"sendMessage('{t}')\" class='btn btn-outline-primary btn-sm m-1'>{t}</button>"
                    for t in time_options
                ])
                return JsonResponse({'response': "Choose your preferred time:<br>" + buttons})

            if step == 'time':
                session['time'] = message
                request.session['chatbot_step'] = 'done'
                request.session.modified = True

                # Save appointment to DB
                AppointmentRequest.objects.create(
                    full_name=session['name'],
                    email=session['email'],
                    phone=session['phone'],
                    preferred_time=session['time'],
                )

                # Send Email Booking
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
                request.session['chatbot_step'] = None
                request.session['chatbot_data'] = {}
                request.session.modified = True
                return JsonResponse({'response': response})

            # Fallback to FAQ
            faq_match = FAQ.objects.filter(question__icontains=message).first()
            if faq_match:
                return JsonResponse({'response': faq_match.answer})

            system_prompt = SystemPrompt.objects.last()
            default_response = system_prompt.prompt_text if system_prompt else "Hi! You can say 'book an appointment' or ask a question."
            return JsonResponse({'response': default_response})

        except json.JSONDecodeError:
            return JsonResponse({'response': "❌ Invalid JSON data."})
    return JsonResponse({'response': "❌ Invalid request method."})

# Funding Options View
def funding_option_view(request):
    funding = get_object_or_404(FundingOptionPage)
    return render(request, 'funding_option.html', {'funding': funding})

# Therapy Methods View
def therapy_methods_list(request):
    therapy_methods = TherapyMethod.objects.all()
    return render(request, 'therapymethods_list.html', {
        'therapy_methods': therapy_methods,
        'media_url': settings.MEDIA_URL
    })

# Detail page for a single therapy method
def therapy_method_detail(request, pk):
    therapy = get_object_or_404(TherapyMethod, pk=pk)
    return render(request, 'therapymethods.html', {
        'therapy': therapy,
        'media_url': settings.MEDIA_URL
    })