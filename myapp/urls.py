from django.urls import path
from . import views
from .views import funding_option_view

urlpatterns = [
    path("", views.index, name="index"),
    path("blog", views.blog, name="blog"),
    path("about/", views.about_us, name="about"),
    path("services", views.services, name="services"),
    path("services/all", views.services_all, name="services_all"),
    path("services/post/<int:id>", views.service_detail, name="service_detail"),
    path("services/create", views.create_service, name="create_service"),
    path("services/edit/<int:id>", views.edit_service, name="edit_service"),
    path("services/delete/<int:id>", views.delete_service, name="delete_service"),
    path('funding/', funding_option_view, name='funding-options'),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout, name="logout"),
    path("create", views.create, name="create"),
    path("increaselikes/<int:id>", views.increaselikes, name="increaselikes"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("profile/edit/<int:id>", views.profileedit, name="profileedit"),
    path("post/<int:id>", views.post, name="post"),
    path("post/comment/<int:id>", views.savecomment, name="savecomment"),
    path("post/comment/delete/<int:id>", views.deletecomment, name="deletecomment"),
    path("post/edit/<int:id>", views.editpost, name="editpost"),
    path("post/delete/<int:id>", views.deletepost, name="deletepost"),
    path("contact", views.contact_us, name="contact"),
    path("chatbot-api/", views.chatbot_api, name="chatbot_api"),
    path('therapy-methods/', views.therapy_methods_list, name='therapy_methods_list'),
    path('therapy-methods/<int:pk>/', views.therapy_method_detail, name='therapy_method_detail'),
    path('footer/', views.footer_view, name='footer_view'),
]