from bx_django_utils.test_utils.html_assertion import (
    HtmlAssertionMixin,
    assert_html_response_snapshot,
)
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponse
from django.test import TestCase, override_settings
from model_bakery import baker


@override_settings(SECURE_SSL_REDIRECT=False)
class FmdWebPageTests(HtmlAssertionMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.normal_user = baker.make(User, is_staff=False, is_active=True, is_superuser=False)

    def test_anonymous(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, template_name='fmd/login_info.html')
        self.assert_html_parts(
            response,
            parts=(
                '<title>Log in | Find My Device</title>',
                '<p class="errornote">To find your device, you must be logged in.</p>',
                '<a href="/admin/login/">Log in</a>',
            ),
        )
        assert_html_response_snapshot(response, query_selector=None, validate=False)

    def test_normal_user(self):
        self.client.force_login(self.normal_user)
        response = self.client.get('/')
        assert isinstance(response, FileResponse)
        response2 = HttpResponse(response.getvalue())
        self.assert_html_parts(
            response2,
            parts=(
                '<title>FMD</title>',
                '<h2>Find My Device</h2>',
                '<link rel="stylesheet" href="/static/fmd_externals/style.css">',
                '<script src="/static/fmd_externals/logic.js"></script>',
            ),
        )
        assert_html_response_snapshot(response2, query_selector=None, validate=False)
