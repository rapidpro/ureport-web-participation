from mock import patch

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

from webparticipation.apps.poll_response.views import poll_response
from webparticipation.apps.ureporter.models import Ureporter


class TestPollResponse(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.uuid = 'cheetahs-flew-over-golf-sanctuariess'
        self.username = 'polling_guy'
        self.password = 'password'
        self.ureporter = Ureporter.objects.create(
            uuid=self.uuid, user=User.objects.create_user(username=self.username, password=self.password))
        self.poll_id = 2

    def tearDown(self):
        self.ureporter.delete()

    @patch('webparticipation.apps.poll_response.views.serve_get_response')
    def test_poll_response_with_get(self, mock_serve_get_response):
        self.client.login(username=self.username, password=self.password)
        request = self.factory.get('/poll/2/respond/')
        request.user = self.ureporter.user
        poll_response(request, self.poll_id)
        mock_serve_get_response.assert_called_once_with(request, self.poll_id)

    @patch('webparticipation.apps.poll_response.views.serve_post_response')
    def test_poll_response_with_post(self, mock_serve_post_response):
        self.client.login(username=self.username, password=self.password)
        request = self.factory.post('/poll/2/respond/')
        request.user = self.ureporter.user
        poll_response(request, self.poll_id)
        mock_serve_post_response.assert_called_once_with(request, self.poll_id)
