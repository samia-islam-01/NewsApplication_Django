from django.shortcuts import render, redirect  # To show HTML pages and redirect users
from django.contrib.auth.models import Group, Permission  # Django's built-in user, group, and permission models
from django.contrib.auth import authenticate, login, logout, get_user_model  # Functions to handle login and logout
from django.http import HttpResponseRedirect, HttpResponse  # For redirecting users or sending responses
from django.urls import reverse, reverse_lazy  # Helps get URLs by their names
from django.contrib.auth.decorators import login_required  # Makes sure only logged-in users can access pages
from datetime import datetime
import secrets  # For generating secure random tokens
from datetime import timedelta
from hashlib import sha1  # To hash tokens securely
from django.core.exceptions import ObjectDoesNotExist  # For handling cases when an object is not found

from .models import ResetToken  # Our custom model to store reset tokens

from django.core.mail import EmailMessage  # To send emails
from django.contrib.auth.hashers import make_password  # To hash passwords before saving

User = get_user_model()


def login_user(request):
    """Handles user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            request.session.set_expiry(60 * 60 * 24 * 30)

            request.session['user_id'] = user.id
            request.session['username'] = user.username

            return HttpResponseRedirect(reverse('authenticator:welcome'))
        else:
            # If login failed, reload login page with an error message
            return render(request, 'authenticator/login.html', {'error': 'Invalid credentials'})

    return render(request, 'authenticator/login.html')


def register_user(request):
    """Handles user registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Password confirmation
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'authenticator/register.html', {
                'error': 'Passwords do not match'
            })

        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            return render(request, 'authenticator/register.html', {
                'error': 'An account with this email address already exists.'
            })

        role = request.POST.get('role')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        if role == 'journalist':
            group, _ = Group.objects.get_or_create(name='Journalist')
        elif role == 'editor':
            group, _ = Group.objects.get_or_create(name='Editor')
        else:
            group, _ = Group.objects.get_or_create(name='Reader')

        user.groups.add(group)

        login(request, user)

        return redirect('authenticator:welcome')

    return render(request, 'authenticator/register.html')


def change_user_password(username, new_password):
    """Handles user password re-creation"""
    user = User.objects.get(username=username)

    user.set_password(new_password)

    user.save()


def logout_user(request):
    """Logs the user out and redirects to login page"""
    if request.user is not None:
        logout(request)  # Log out the current user
        return HttpResponseRedirect(reverse('authenticator:login'))


@login_required(login_url=reverse_lazy('authenticator:login'))
def welcome(request):
    """Only logged-in users can see the welcome page"""
    return render(request, 'authenticator/welcome.html')


def build_email(user, reset_url):
    """Builds email for password reset"""
    subject = "Password Reset"
    user_email = user.email
    domain_email = "example@domain.com"  # The "from" email address for the email
    body = f"Hi {user.username},\nHere is your link to reset your password: \n{reset_url}"

    email = EmailMessage(subject, body, domain_email, [user_email])
    return email


def generate_reset_url(user):
    """Creates a secure generate reset url that expires in 5 minutes"""
    domain = "http://127.0.0.1:8000/"
    url = f"{domain}/reset/"

    token = secrets.token_urlsafe(16)  # Generate a random secure token

    expiry_date = datetime.now() + timedelta(minutes=5)  # Token expires in 5 minutes

    hashed_token = sha1(token.encode()).hexdigest()  # Hash the token to store securely

    ResetToken.objects.create(
        user=user,
        token=hashed_token,
        expiry_date=expiry_date
    )

    url += f"{token}/"
    print(url)
    print(token)
    print(hashed_token)
    return url


def send_password_reset(request):
    """Handles sending the password reset email after user submits their email"""
    if request.method == 'POST':
        user_email = request.POST.get('email')
        try:
            user = User.objects.get(email=user_email)
            reset_url = generate_reset_url(user)  # Generate reset link with token
            email = build_email(user, reset_url)  # Create the email message
            email.send()

            # Show a confirmation page that email was sent
            return render(request, 'authenticator/reset_email_sent.html', {
                'email': user_email
            })

        except ObjectDoesNotExist:
            # Even if no user found, still show confirmation (to avoid info leaks)
            return render(request, 'authenticator/reset_email_sent.html', {
                'email': user_email
            })

    # Show the form where user can enter their email
    return render(request, 'authenticator/request_password_reset.html')


def reset_user_password(request, token):
    """Handles resetting user password when the user clicks the link in their email"""
    hashed_token = sha1(token.encode()).hexdigest()  # Hash the token from URL

    try:
        user_token = ResetToken.objects.get(token=hashed_token)  # Look for token in DB

        # Check if the token expired
        if user_token.expiry_date.replace(tzinfo=None) < datetime.now():
            user_token.delete()  # Delete expired token
            return render(request, 'authenticator/password_reset_expired.html')  # Show expired token message

        request.session['user_id'] = user_token.user.id
        request.session['reset_token'] = token

        return render(request, 'authenticator/password_reset.html', {'token': token})

    except ResetToken.DoesNotExist:
        # Token not found or already used
        return render(request, 'authenticator/password_reset_invalid.html')


def reset_password(request):
    """Handles the password reset form submission (when user enters new password)"""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        token = request.session.get('reset_token')
        password = request.POST.get('password')
        password_conf = request.POST.get('password_conf')

        # Check if all required data is present
        if not all([user_id, token, password, password_conf]):
            print(token)
            print(password)
            return render(request, 'password_reset.html', {
                'error': 'Missing fields or session expired.',
                'token': token
            })

        # Check if passwords match
        if password != password_conf:
            return render(request, 'password_reset.html', {
                'error': 'Passwords do not match.',
                'token': token
            })

        try:
            user = User.objects.get(id=user_id)
            hashed_token = sha1(token.encode()).hexdigest()
            reset_token = ResetToken.objects.get(token=hashed_token)

            # Check token expiry again
            if reset_token.expiry_date.replace(tzinfo=None) < datetime.now():
                reset_token.delete()
                return render(request, 'password_reset_expired.html')

            # Update the user's password (hashed securely)
            user.password = make_password(password)
            user.save()

            # Delete the token and clear session info
            reset_token.delete()
            request.session.flush()

            return HttpResponseRedirect(reverse('authenticator:login'))

        except (User.DoesNotExist, ResetToken.DoesNotExist):
            return render(request, 'password_reset_invalid.html')

    return HttpResponseRedirect(reverse('authenticator:login'))