from django.conf import settings
import requests
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext as _

from webparticipation.apps.ureporter.models import Ureporter
from webparticipation.apps.rapidpro_receptor.views import send_message_to_rapidpro, get_messages_for_user


@login_required
def poll_response(request, poll_id):
    username = str(request.user)
    uuid = Ureporter.objects.get(user__username=username).uuid
    flow_info = get_flow_info_from_poll_id(request, poll_id)
    if request.method == 'GET':
        return serve_get_response(request, poll_id, flow_info, username, uuid)
    if request.method == 'POST':
        return serve_post_response(request, poll_id, flow_info, username, uuid)


@login_required
def latest_poll_response(request):
    response = requests.get(settings.UREPORT_ROOT +
                            '/api/v1/polls/org/' + settings.UREPORT_ORG_ID + '/featured/')
    response_json = response.json()
    if response_json['count']:
        latest_poll_id = response_json['results'][0]['id']
        return poll_response(request, latest_poll_id)
    else:
        return render(request, 'poll_response.html', {
            'messages': [{'msg_text': _("There is no current poll available.")}],
            'is_complete': True,
            'no_latest': True,
            'submission': request.POST.get('send')})
        HttpResponseNotFound('No latest poll')


def get_flow_info_from_poll_id(request, poll_id):
    response = requests.get(settings.UREPORT_ROOT + '/api/v1/polls/' + str(poll_id) + '/')
    flow_info = response.json()
    return flow_info


def serve_get_response(request, poll_id, flow_info, username, uuid):
    if is_run_complete(flow_info['flow_uuid'], uuid):
        return serve_already_taken_poll_message(request, poll_id, flow_info)
    trigger_flow_run(flow_info['flow_uuid'], uuid)
    messages = get_messages_for_user(username)
    title = flow_info['title']
    return render(request, 'poll_response.html', {'messages': messages, 'poll_id': poll_id, 'title': title})


def serve_already_taken_poll_message(request, poll_id, flow_info):
    return render(request, 'poll_response.html', {
        'messages': [_("You've already taken this poll.")],
        'poll_id': poll_id,
        'title': flow_info['title'],
        'is_complete': True,
        'submission': request.POST.get('send')})


def trigger_flow_run(flow_uuid, uuid):
    api_path = settings.RAPIDPRO_API_PATH
    rapidpro_api_token = settings.RAPIDPRO_API_TOKEN
    requests.post(api_path + '/runs.json',
                  data={'flow_uuid': flow_uuid, 'contacts': uuid},
                  headers={'Authorization': 'Token ' + rapidpro_api_token})


def serve_post_response(request, poll_id, flow_info, username, uuid):
    send_message_to_rapidpro({'from': username, 'text': request.POST['send']})
    run_is_complete = is_run_complete(flow_info['flow_uuid'], uuid)
    if run_is_complete:
        save_last_poll_taken(username, poll_id)
    msgs = get_messages_for_user(username)
    title = flow_info['title']
    return render(request, 'poll_response.html', {
        'messages': msgs,
        'poll_id': poll_id,
        'title': title,
        'is_complete': run_is_complete,
        'submission': request.POST.get('send')})


def is_run_complete(flow_uuid, uuid):
    api_path = settings.RAPIDPRO_API_PATH
    rapidpro_api_token = settings.RAPIDPRO_API_TOKEN
    runs = requests.get(api_path + '/runs.json?flow_uuid=' + flow_uuid + '&contact=' + uuid,
                        headers={'Authorization': 'Token ' + rapidpro_api_token})
    return bool([run['completed'] for run in runs.json()['results'] if run['completed'] is True])


def save_last_poll_taken(username, poll_id):
    ureporter = Ureporter.objects.get(user__username=username)
    ureporter.last_poll_taken = poll_id
    ureporter.save()
