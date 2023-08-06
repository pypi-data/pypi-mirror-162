from django.utils.encoding import force_str
from typing import List, Dict, Any, Type, Union
from model_admin.hooks.buttons.components import Button, AddButton


class BaseButtonHelper:
    buttons: List[Type[Button]]
    _add_button: Type[Button] = AddButton

    def __init__(self, view, request):
        self.view = view
        self.request = request
        self.model = view.model
        self.opts = view.model._meta
        self.verbose_name = force_str(self.opts.verbose_name)
        self.verbose_name_plural = force_str(self.opts.verbose_name_plural)
        self.permission_helper = view.permission_helper
        self.url_helper = view.url_helper

    def get_add_button(self):
        return self._add_button().render(self)

    def _render(self,
                button: Type[Button],
                pk: str,
                classnames_add: List[str],
                classnames_exclude: List[str]) -> Dict[str, Any]:
        """Render the button from the given values

        Args:
            button (Type[Button): The button that will be rendered
            pk (str): The ID of current object
            classnames_add (List[str]): A list of css classes to render
            classnames_exclude (List[str]): A list of css classes to exclude from the render

        Returns:
            A dict containing all data to render de button
        """
        return button().render(
            helper=self,
            pk=pk,
            classnames_add=classnames_add,
            classnames_exclude=classnames_exclude
        ).to_dict()

    @staticmethod
    def _parse_none(value: Union[None, list] = None) -> list:
        """ Parse nones values
        Args:
            value (Union[None, list]): A value to be converted

        Returns:
            A list
        """
        return [] if value is None else value

    def _get_pk(self, obj):
        return getattr(obj, self.opts.pk.attname)

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None,
                            classnames_exclude=None):
        """Fetch all buttons defined in self._buttons, validate and append to a list of buttons.

        This list will be passed to wagtail that will render all of them.

        Args:
            obj: The current object
            exclude: Buttons to exclude when render
             classnames_add (List[str]): A list of css classes to render
            classnames_exclude (List[str]): A list of css classes to exclude from the render

        Returns:
            A list of buttons
        """
        pk = self._get_pk(obj)
        buttons = []
        for button in self.buttons:
            if button.validate(self.permission_helper, self.request, obj, self._parse_none(exclude)):
                buttons.append(
                    self._render(
                        button,
                        pk,
                        self._parse_none(classnames_add),
                        self._parse_none(classnames_exclude)
                    )
                )
        return buttons
