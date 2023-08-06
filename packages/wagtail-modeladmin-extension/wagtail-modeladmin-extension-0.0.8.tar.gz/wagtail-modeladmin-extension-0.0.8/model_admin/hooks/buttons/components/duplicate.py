from django.contrib.admin.utils import quote
from django.utils.translation import gettext as _

from model_admin.hooks.buttons.components import Button
from model_admin.hooks.buttons.entity.button import ButtonEntity


class DuplicateButton(Button):

    @staticmethod
    def validate(permission_helper, request, obj, exclude) -> bool:
        return 'duplicate' not in exclude and \
               permission_helper.user_can_edit_obj(request.user, obj)

    def render(self, helper, pk, classnames_add=None, classnames_exclude=None, *args, **kwargs) -> ButtonEntity:
        return ButtonEntity(
            url=helper.url_helper.get_action_url('duplicate', quote(pk)),
            label=_('Duplicate'),
            classname=self._get_classnames(classnames_add, classnames_exclude),
            title=_('Duplicate this %s') % helper.verbose_name,
        )
