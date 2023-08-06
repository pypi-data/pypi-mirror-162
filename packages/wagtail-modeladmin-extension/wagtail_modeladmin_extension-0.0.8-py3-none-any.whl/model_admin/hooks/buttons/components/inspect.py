from django.contrib.admin.utils import quote

from .base import Button
from django.utils.translation import gettext as _
from model_admin.hooks.buttons.entity.button import ButtonEntity


class InspectButton(Button):

    @staticmethod
    def validate(permission_helper, request, obj, exclude) -> bool:
        return 'inspect' not in exclude and permission_helper.user_can_inspect_obj(request.user, obj)

    def render(self, helper, pk, classnames_add=None, classnames_exclude=None, *args, **kwargs) -> ButtonEntity:
        return ButtonEntity(
            url=helper.url_helper.get_action_url('inspect', quote(pk)),
            label=_('Inspect'),
            classname=self._get_classnames(classnames_add, classnames_exclude),
            title=_('Inspect this %s') % helper.verbose_name,
        )
