from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import UserProfile, EmailOTP,Vote,Campaign,Candidate
from .utils import generate_otp,send_otp_email
from django.db import transaction
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from datetime import timedelta
import random


# Home page for all
def home(request):
    return render(request, "home.html")

# regster for Users
def register(request):
    if request.user.is_authenticated:
        return redirect("/campaigns-page/")

    if request.method == "GET":
        return render(request, "register.html")

    if request.method != "POST":
        return HttpResponse("Method not allowed")

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    full_name = request.POST.get('full_name')
    roll_number = request.POST.get('roll_number')

    if not all([username, email, password, full_name, roll_number]):
        return HttpResponse("All fields are required")

    if User.objects.filter(username=username).exists():
        return HttpResponse("Username already exists")

    if User.objects.filter(email=email).exists():
        return HttpResponse("Email already exists")

    if UserProfile.objects.filter(roll_number=roll_number).exists():
        return HttpResponse("Roll number already exists")

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )

            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                roll_number=roll_number
            )

            otp = generate_otp()
            EmailOTP.objects.create(user=user, otp=otp)
            send_otp_email(email, otp, user=user)

    except Exception:
        return HttpResponse("Registration failed. Please try again.")

    request.session['otp_user_id'] = user.id
    return redirect("verify_otp")

# login for user 
def user_login(request):    
    # ✅ PREVENT LOGGED-IN USERS FROM SEEING LOGIN PAGE
    if request.user.is_authenticated:
        return redirect("/campaigns-page/")

    if request.method == "GET":
        return render(request, "login.html")

    if request.method != "POST":
        return HttpResponse("POST only")

    user = authenticate(
        request,
        username=request.POST.get('username'),
        password=request.POST.get('password')
    )

    if not user:
        return render(request, "login.html", {"error": "Invalid credentials"})

    if not user.is_active:
        return render(request, "login.html", {"error": "Email not verified"})

    login(request, user)
    return redirect("/campaigns-page/")

# user logout
def user_logout(request):
    logout(request)
    return redirect("home")

# user registation otp verification
def verify_otp(request):
    if request.method == "GET":
        return render(request, "verify_otp.html")

    if request.method == "POST":
        user_id = request.session.get("otp_user_id")
        otp_purpose = request.session.get("otp_purpose")
        entered_otp = request.POST.get("otp")

        if not user_id or not entered_otp:
            return HttpResponse("Invalid request")

        try:
            user = User.objects.get(id=user_id)
            record = EmailOTP.objects.get(user=user)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return HttpResponse("Invalid session or OTP")

        if record.is_verified:
            return HttpResponse("Already verified")

        if record.otp != entered_otp:
            return HttpResponse("Invalid OTP")

        user.is_active = True
        user.save()

        record.is_verified = True
        record.save()

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_purpose", None)

        if otp_purpose == "edit_profile":
            login(request, user)  # ensure session is active
            return redirect("/campaigns-page/")

        return redirect("login")

    return HttpResponse("Method not allowed")

# campaign list view for users and admin also 
def campaign_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    campaigns = Campaign.objects.filter(is_active=True)
    data = list(campaigns.values(
        'id',
        'title',
        'description',
        'start_date',
        'end_date'
    ))
    return JsonResponse(data, safe=False)

# user must be login for vote 
@login_required
def vote(request, campaign_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    # Prevent multiple votes
    if Vote.objects.filter(user=request.user, campaign_id=campaign_id).exists():
        return JsonResponse({"error": "Already voted"}, status=409)

    # Validate campaign status and time window
    campaign = Campaign.objects.filter(
        id=campaign_id,
        is_active=True,
        start_date__lte=now(),
        end_date__gte=now()
    ).first()

    if not campaign:
        return JsonResponse(
            {"error": "Campaign not active or voting period ended"},
            status=403
        )

    candidate_id = request.POST.get("candidate_id")
    if not candidate_id:
        return JsonResponse({"error": "Candidate ID required"}, status=400)

    # Ensure candidate belongs to campaign
    if not Candidate.objects.filter(
        id=candidate_id,
        campaign_id=campaign_id
    ).exists():
        return JsonResponse({"error": "Invalid candidate"}, status=400)

    Vote.objects.create(
        user=request.user,
        campaign_id=campaign_id,
        candidate_id=candidate_id
    )

    return JsonResponse({"message": "Vote submitted successfully"})

# user can view the candidates for the specific campagin 
@login_required
def candidate_list(request, campaign_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    campaign = Campaign.objects.filter(
        id=campaign_id,
        is_active=True,
        start_date__lte=now(),
        end_date__gte=now()
    ).first()

    if not campaign:
        return JsonResponse({"error": "Campaign not active"}, status=404)

    candidates = Candidate.objects.filter(campaign=campaign)

    vote = Vote.objects.filter(
        user=request.user,
        campaign=campaign
    ).first()

    data = {
        "has_voted": bool(vote),
        "voted_candidate_id": vote.candidate_id if vote else None,
        "candidates": list(candidates.values("id", "name", "party"))
    }

    return JsonResponse(data)

# hetting the campagin page
@login_required
def campaigns_page(request):
    
    return render(request, "campaigns.html")

# candidate page for user 
@login_required
def candidates_page(request, campaign_id):
    return render(request, "candidates.html", {
        "campaign_id": campaign_id
    })

# resuls page
def results(request, campaign_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    campaign = Campaign.objects.filter(
        id=campaign_id,
        is_active=True
    ).first()

    if not campaign:
        return JsonResponse({"error": "Campaign not found or inactive"}, status=404)

    today = timezone.now().date()
    if today <= campaign.end_date.date():
        return JsonResponse(
            {
                "message": "Results will be available after the campaign ends",
                "end_date": campaign.end_date
            },
            status=403
        )

    candidates = (
        Candidate.objects
        .filter(campaign_id=campaign_id)
        .annotate(total_votes=Count('vote'))
        .values('id', 'name', 'party', 'total_votes')
    )

    return JsonResponse(list(candidates), safe=False)

# result pages
@login_required
def results_page(request, campaign_id):
    return render(request, "results.html", {
        "campaign_id": campaign_id
    })


# edit profile
@login_required
def edit_profile(request):
    user = request.user
    profile = user.userprofile

    if request.method == "POST":
        new_email = request.POST.get("email")
        full_name = request.POST.get("full_name")

        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        email_changed = new_email != user.email

        # PASSWORD CHANGE (OPTIONAL)
        if old_password or new_password:
            if not old_password or not new_password:
                messages.error(request, "Both old and new passwords are required")
                return redirect("edit_profile")

            if not user.check_password(old_password):
                messages.error(request, "Old password is incorrect")
                return redirect("edit_profile")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect("edit_profile")

            user.set_password(new_password)
            update_session_auth_hash(request, user)  # keep user logged in

        # UPDATE BASIC PROFILE
        profile.full_name = full_name

        # EMAIL CHANGE → OTP VERIFICATION
        if email_changed:
            otp = generate_otp()

            # Save OTP
            EmailOTP.objects.update_or_create(
                user=user,
                defaults={
                    "otp": otp,
                    "is_verified": False
                }
            )

            # Update email but deactivate user
            user.email = new_email
            user.is_active = False
            user.save()
            profile.save()

            # Store OTP context
            request.session["otp_user_id"] = user.id
            request.session["otp_purpose"] = "edit_profile"

            # Send OTP using existing util
            send_otp_email(new_email, otp)

            return redirect("verify_otp")

        # NORMAL UPDATE (NO EMAIL CHANGE)
        user.email = new_email
        user.save()
        profile.save()

        return redirect("/campaigns-page/")

    return render(request, "edit_profile.html", {
        "user": user,
        "profile": profile
    })


# resend otp
def resend_otp(request):
    if request.method != "POST":
        return redirect("verify_otp")

    user_id = request.session.get("otp_user_id")

    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect("register")

    # Generate new OTP
    otp = str(random.randint(100000, 999999))

    EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp": otp,
            "is_verified": False,
            "created_at": timezone.now()
        }
    )

    # Send OTP
    try:
        send_otp_email(user.email, otp, user)
        messages.success(request, "New OTP sent to your email.")
    except Exception:
        messages.error(
            request,
            "Failed to send OTP. Admin has been notified."
        )

    return redirect("verify_otp")



# update email by otp verfication
def update_email_otp(request):
    if request.method != "POST":
        return redirect("verify_otp")

    user_id = request.session.get("otp_user_id")

    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect("register")

    new_email = request.POST.get("email")

    if not new_email:
        messages.error(request, "Email is required")
        return redirect("verify_otp")

    #  Update email & deactivate
    user.email = new_email
    user.is_active = False
    user.save()

    #  Generate OTP
    otp = str(random.randint(100000, 999999))

    EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp": otp,
            "is_verified": False,
            "created_at": timezone.now()
        }
    )

    #  Send OTP
    try:
        send_otp_email(new_email, otp, user)
        messages.success(request, "OTP sent to updated email address")
    except Exception:
        messages.error(
            request,
            "OTP could not be delivered. Admin has been notified."
        )

    return redirect("verify_otp")
