import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.static import serve

from findmydevice import WEB_PATH


logger = logging.getLogger(__name__)


class FmdWebPageView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'fmd/login_info.html'

    def get(self, request):
        logger.debug('Serve FMD index.html')
        return serve(request, path='/index.html', document_root=WEB_PATH, show_indexes=False)

    def handle_no_permission(self):
        return self.render_to_response(
            context=dict(
                title=_('Log in'),
                site_title='Find My Device',
                loging_url=self.get_login_url(),
            )
        )
