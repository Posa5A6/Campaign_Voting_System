from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Authentication
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path("resend-otp/", views.resend_otp, name="resend_otp"), 
    path("update-email-otp/", views.update_email_otp, name="update_email_otp"),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("edit-profile/", views.edit_profile, name="edit_profile"),

    # Campaign APIs
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path('candidates/<int:campaign_id>/', views.candidate_list, name='candidates'),
    path('vote/<int:campaign_id>/', views.vote, name='vote'),
    path('results/<int:campaign_id>/', views.results, name='results'),
    
    path("results-page/<int:campaign_id>/", views.results_page, name="results_page"),
    path('campaigns-page/', views.campaigns_page, name='campaigns_page'),
    path('campaign/<int:campaign_id>/candidates/', views.candidates_page, name='candidates_page'),
    path("candidates-page/<int:campaign_id>/", views.candidates_page),
    path("campaign/<int:campaign_id>/candidates/", views.candidates_page, name="candidates_page"),


    

]
