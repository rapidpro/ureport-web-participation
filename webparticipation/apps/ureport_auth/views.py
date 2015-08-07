from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.utils import timezone
from webparticipation.apps.ureport_auth.models import PasswordReset
from webparticipation.apps.ureport_auth.tasks import send_forgot_password_email
from webparticipation.apps.ureporter.models import Ureporter
from webparticipation.apps.utils.views import is_valid_password


def login_user(request):
    backend = 'django.contrib.auth.backends.ModelBackend'

    if request.method == 'GET':
        redirect_to = request.GET.get('next', '/')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        redirect_to = request.POST.get('next', '/home')
        user = None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, 'There is no registered '
                                      'user with sign-in email ' + email)
        if user:
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user is not None:
                authenticated_user.backend = backend
                if user.is_active:
                    login(request, authenticated_user)
                    return HttpResponseRedirect(redirect_to)
            else:
                messages.error(request, 'Password is incorrect')

    return render_to_response('login.html', RequestContext(request, {'next': redirect_to}))


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user:
                send_forgot_password_email.delay(email)
                return render(request, 'forgot_password.html', {
                    'success_message': 'We have sent an email to ' + email + ' with recovery instructions. ' +
                                'Please check your email.',
                    'password_reset_email_sent': True})
        except User.DoesNotExist:
            messages.error(request, 'There is no registered user with sign-in email ' + email)
    return render_to_response('forgot_password.html', RequestContext(request))


def password_reset(request, user_uuid):
    ureport_user = Ureporter.objects.get(uuid=user_uuid)
    user = User.objects.get(id=ureport_user.user_id)
    reset = PasswordReset.objects.get(user_id=user.id)
    if request.method == 'GET':
        if not reset.expiry > timezone.now():
            messages.error(request, 'Sorry that recovery '
                                    'link is expired. Please Try again.')
            return HttpResponseRedirect('/forgot-password/')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if is_valid_password(password):
                user.save()
                messages.info(request, 'Password successfully '
                                       'changed for ' + ureport_user.user.email)
                return HttpResponseRedirect('/login/')

            else:
                messages.error(request, 'Password should have a minimum of '
                                        '8 characters '
                                        'which should contain at least one '
                                        'uppercase, lowercase, '
                                        'number and special character.')
        else:
            messages.error(request, 'Password do not match.')
    return render_to_response('password_reset.html', RequestContext(request))
