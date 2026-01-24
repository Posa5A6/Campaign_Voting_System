from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from .models import Campaign, Candidate, Vote
from django.db.models import Count
from django.utils.timezone import make_aware, get_current_timezone
from django.utils.timezone import now, localtime
from django.http import HttpResponseForbidden


# checking is admin or not 
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


admin_required = user_passes_test(
    is_admin,
    login_url="admin_login",
    redirect_field_name="next"
)

# admin login 
@csrf_protect
def admin_login(request):
    if request.method == "GET":
        return render(request, "admin/login.html")

    user = authenticate(
        request,
        username=request.POST.get("username"),
        password=request.POST.get("password")
    )

    if not user or not (user.is_staff or user.is_superuser):
        return render(request, "admin/login.html", {"error": "Invalid admin credentials"})

    login(request, user)

    nxt = request.GET.get("next")
    return redirect(nxt) if nxt else redirect("admin_dashboard")


# admin logout 
def admin_logout(request):
    logout(request)
    return redirect("admin_login")


# admin dashboard 
@user_passes_test(is_admin)
def admin_dashboard(request):
    # auto mark ended campaigns inactive (optional)
    Campaign.objects.filter(is_active=True, end_date__lt=now()).update(is_active=False)

    return render(request, "admin/dashboard.html", {
        "campaign_count": Campaign.objects.count(),
        "vote_count": Vote.objects.count(),
        "active_campaigns": Campaign.objects.filter(is_active=True).count(),
        "recent_campaigns": Campaign.objects.order_by("-id")[:5],
        "now": now(),
    })



# admin campaigns
@admin_required
def admin_campaigns(request):
    Campaign.objects.filter(is_active=True, end_date__lt=now()).update(is_active=False)
    current = localtime(now())
    campaigns = Campaign.objects.all().order_by("-id")

    for c in campaigns:
        start = localtime(c.start_date)
        end = localtime(c.end_date)
        if not c.is_active:
            c.status_label = "Inactive"
        elif start > current:
            c.status_label = "Upcoming"
        elif end < current:
            c.status_label = "Ended"
        else:
            c.status_label = "Live"

    return render(request, "admin/campaigns.html", {"campaigns": campaigns, "now": now()})

# create campaign 
@csrf_protect
@admin_required
def create_campaign(request):
    if request.method == "GET":
        return render(request, "admin/create_campaign.html")

    title = request.POST.get("title")
    description = request.POST.get("description")
    start_raw = request.POST.get("start_date")
    end_raw = request.POST.get("end_date")

    if not all([title, description, start_raw, end_raw]):
        messages.error(request, "All fields are required")
        return redirect("create_campaign")

    start_dt = parse_datetime(start_raw)
    end_dt = parse_datetime(end_raw)

    tz = get_current_timezone()

    # datetime-local gives naive -> make it IST aware
    if start_dt and start_dt.tzinfo is None:
        start_dt = make_aware(start_dt, tz)

    if end_dt and end_dt.tzinfo is None:
        end_dt = make_aware(end_dt, tz)

    if not start_dt or not end_dt:
        messages.error(request, "Invalid date format")
        return redirect("create_campaign")

    if end_dt <= start_dt:
        messages.error(request, "End time must be after start time")
        return redirect("create_campaign")

    Campaign.objects.create(
        title=title,
        description=description,
        start_date=start_dt,
        end_date=end_dt,
        is_active=True
    )

    messages.success(request, "Campaign created successfully")
    return redirect("admin_campaigns")

# delete campaign 
@admin_required
@require_POST
def delete_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    campaign.delete()
    messages.success(request, "Campaign deleted.")
    return redirect("admin_campaigns")

# admin candies add 
@admin_required
def admin_candidates(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    candidates = Candidate.objects.filter(campaign=campaign)
    return render(request, "admin/candidates.html", {
        "campaign": campaign,
        "candidates": candidates
    })


# add candidates to admin
@admin_required
@csrf_protect
def add_candidate(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == "GET":
        return render(request, "admin/add_candidate.html", {"campaign": campaign})

    name = request.POST.get("name", "").strip()
    party = request.POST.get("party", "").strip()

    if not name or not party:
        messages.error(request, "Candidate name and party are required.")
        return redirect("add_candidate", campaign_id=campaign.id)

    Candidate.objects.create(campaign=campaign, name=name, party=party)
    messages.success(request, "Candidate added successfully.")
    return redirect("admin_candidates", campaign_id=campaign.id)

# admin results 
@admin_required
def admin_results(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    results = (
        Candidate.objects
        .filter(campaign=campaign)
        .annotate(total_votes=Count("vote"))
        .order_by("-total_votes")
    )

    return render(request, "admin/results.html", {
        "campaign": campaign,
        "results": results,
        "ended": campaign.end_date < now()
    })

# delete candidates 
@user_passes_test(is_admin)
def delete_candidate(request, candidate_id):
    if request.method != "POST":
        return HttpResponseForbidden("POST only")

    candidate = get_object_or_404(Candidate, id=candidate_id)
    campaign_id = candidate.campaign_id  # so we can redirect back
    candidate.delete()

    return redirect("admin_candidates", campaign_id=campaign_id)
