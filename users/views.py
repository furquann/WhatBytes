from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import PasswordReset
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username')
        password = request.POST.get('password')

        # Check if the input is an email or username
        user = None
        if '@' in email_or_username:  # It's likely an email
            try:
                user = User.objects.get(email=email_or_username)
            except User.DoesNotExist:
                user = None
        else:  # It's likely a username
            user = User.objects.filter(username=email_or_username).first()

        # Authenticate user if found
        if user is not None:
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')



def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if is_strong_password(password):
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.success(request, 'Account created successfully!')
                    return redirect('login')
                else:
                    messages.error(request, 'Username already exists')
            else:
                messages.error(request, 'Password is not strong enough. It should be at least 8 characters long and contain an uppercase letter, a lowercase letter, a digit, and a special character.')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'users/signup.html')



def user_logout(request):
    logout(request)
    return redirect('login')



def forgot_password(request):

    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # create a new reset id
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            # creat password reset ur;
            password_reset_url = reverse('reset_password', kwargs={'reset_id': new_password_reset.reset_id})

            domain_name = "http://127.0.0.1:8000"
            # email content
            email_body = f"Reset your password using the link below:\n\n\n{domain_name}{password_reset_url}"

            email_message = EmailMessage(
                'Reset your password', 
                email_body,
                settings.EMAIL_HOST_USER, 
                [email] 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password_reset_sent', reset_id=new_password_reset.reset_id)



        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot_password')
        
    return render(request, 'users/forgot_password.html')


def password_reset_sent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'users/password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot_password')



# def reset_password(request):
#     try:
#         reset_id = PasswordReset.objects.get(reset_id=reset_id)

#         if request.method == 'POST':

#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirm_password')

#             passwords_have_error = False

#             if password != confirm_password:
#                 passwords_have_error = True
#                 messages.error(request, 'Passwords do not match')
            
#             is_strong_password = is_strong_password(password)

#             if not is_strong_password:
#                 passwords_have_error = True
#                 messages.error(request, "Make sure you keep a strong password. It must be atleast 8 characters long and with atleast one capital letter and a symbol")

#             expiration_time = reset_id.created_when + timezone.timedelta(minutes=10)

#             if timezone.now() > expiration_time:
#                 passwords_have_error = True
#                 messages.error(request, 'Reset link has expired')

#             # reset password
#             if not passwords_have_error:
#                 user = reset_id.user
#                 user.set_password(password)
#                 user.save()
                
#                 # delete reset id after use
#                 reset_id.delete()

#                 # redirect to login
#                 messages.success(request, 'Password reset. Proceed to login')
#                 return redirect('login')

#     except PasswordReset.DoesNotExist:
#         messages.error(request, 'Invalid reset id')
#         return redirect('forgot_password')
    
#     return render(request, 'users/reset_password.html')

def reset_password(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset_password', reset_id=reset_id)

    
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot_password')

    return render(request, 'users/reset_password.html')


def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
        elif not is_strong_password(new_password1): 
            messages.error(request, "Your new password is not strong enough.")
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user) 
            messages.success(request, "Your password has been changed successfully!")
            return redirect('dashboard')

    return render(request, 'users/change_password.html')



def is_strong_password(password):

    if len(password) < 8:
        return False
    
    # Check if password contains at least one lowercase letter, one uppercase letter, one digit, and one special character
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

