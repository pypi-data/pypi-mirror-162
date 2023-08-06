from .base import Button
from django.utils.translation import gettext as _
from model_admin.hooks.buttons.entity.button import ButtonEntity


class AddButton(Button):
    custom_classnames = ['bicolor', 'icon', 'icon-plus']

    def render(self, helper, classnames_add=None, classnames_exclude=None, *args, **kwargs) -> ButtonEntity:
        return ButtonEntity(
            url=helper.url_helper.create_url,
            label=_('Add %s') % helper.verbose_name,
            classname=self._get_classnames(classnames_add, classnames_exclude),
            title=_('Add a new %s') % helper.verbose_name,
        )
