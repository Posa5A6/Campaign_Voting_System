from django.urls import path
from . import views_admin

urlpatterns = [
    path("login/", views_admin.admin_login, name="admin_login"),
    path("logout/", views_admin.admin_logout, name="admin_logout"),
    path("dashboard/", views_admin.admin_dashboard, name="admin_dashboard"),

    path("campaigns/", views_admin.admin_campaigns, name="admin_campaigns"),
    path("campaigns/create/", views_admin.create_campaign, name="create_campaign"),
    path("campaigns/delete/<int:campaign_id>/", views_admin.delete_campaign, name="delete_campaign"),
    path("candidates/<int:campaign_id>/", views_admin.admin_candidates, name="admin_candidates"),
    path("candidates/add/<int:campaign_id>/", views_admin.add_candidate, name="add_candidate"),
    path("candidates/delete/<int:candidate_id>/", views_admin.delete_candidate, name="delete_candidate"),
    path("results/<int:campaign_id>/", views_admin.admin_results, name="admin_results"),
]
