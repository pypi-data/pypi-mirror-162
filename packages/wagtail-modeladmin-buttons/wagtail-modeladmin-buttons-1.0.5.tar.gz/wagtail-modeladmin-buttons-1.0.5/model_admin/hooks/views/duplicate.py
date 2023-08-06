from django.shortcuts import redirect
from wagtail.admin import messages
from wagtail.contrib.modeladmin.views import InstanceSpecificView
from django.utils.translation import gettext as _

from model_admin.utils.duplicate import DuplicateObject


class DuplicateView(InstanceSpecificView):
    page_title = _('Duplicate')

    def confirmation_message(self):
        return _(
            "Are you sure you want to duplicate this %s?"
        ) % self.verbose_name

    def duplicate_url(self):
        return self.url_helper.get_action_url('duplicate', self.pk_quoted)

    def post(self, request, *args, **kwargs):
        msg = _("%(model_name)s '%(instance)s' duplicated.") % {
            'model_name': self.verbose_name, 'instance': self.instance
        }
        DuplicateObject.do(self.instance)
        messages.success(request, msg)
        return redirect(self.index_url)

    def get_template_names(self):
        return self.model_admin.get_duplicate_template()
