from unittest.mock import Mock
from model_admin.hooks.buttons.components import AddButton, Button
from model_admin.hooks.buttons.helpers.base import BaseButtonHelper
from model_admin.hooks.buttons.helpers.default import DefaultButtonHelper
from model_admin.tests.hooks.buttons.test_base.base import TestBaseButtons


class TestBaseHelper(TestBaseButtons):

    def setUp(self):
        super().setUp()

        self.request = Mock()
        self.c = BaseButtonHelper(self.view, self.request)
        self.c.buttons = [AddButton]

    def test_get_add_button(self):
        """Should return a button Rendered"""

        expected = {
            "url": 'add.url',
            "label": 'Add Helper',
            "classname": 'button bicolor icon icon-plus',
            "title": 'Add a new Helper'
        }

        self.assertEqual(expected, self.c.get_add_button().to_dict())

    def test_render(self):
        """Should render a button"""
        button = AddButton
        pk = "bla"
        result = self.c._render(button, pk, [], [])
        expected = {
            "url": 'add.url',
            "label": 'Add Helper',
            "classname": 'button bicolor icon icon-plus',
            "title": 'Add a new Helper'
        }

        self.assertEqual(expected, result)

    def test_return_list_if_value_is_none(self):
        """Should return a empty list if the value is none"""
        value = None
        result = self.c._parse_none(value)
        expected = []

        self.assertEqual(result, expected)

    def test_return_the_value_if_is_non_empty_list(self):
        """Should return the list with values"""
        value = ["teste"]
        result = self.c._parse_none(value)
        expected = ["teste"]

        self.assertEqual(expected, result)

    def test_get_pk(self, ):
        """Must return the correct ID. """
        result = self.c._get_pk(obj=self.obj)
        expected = "UUID_QUALQUER"

        self.assertEqual(result, expected)

    def test_get_buttons_for_obj(self):
        """Should return all buttons as a list of dicts"""
        result = self.c.get_buttons_for_obj(obj=self.obj)
        expected = [
            {
                "url": 'add.url',
                "label": 'Add Helper',
                "classname": 'button bicolor icon icon-plus',
                "title": 'Add a new Helper'
            }
        ]
        self.assertEqual(result, expected)

    def test_not_implemented_render(self):
        """Should raises a NotImplemented Error if a class without render method was defined"""

        class TestButton(Button): # noqa
            pass

        with self.assertRaises(NotImplementedError):
            b = TestButton()
            b.render(helper=Mock(), pk="BLA")

    def test_default_button(self):
        """Render the default buttons"""
        DefaultButtonHelper(self.view, self.request)
