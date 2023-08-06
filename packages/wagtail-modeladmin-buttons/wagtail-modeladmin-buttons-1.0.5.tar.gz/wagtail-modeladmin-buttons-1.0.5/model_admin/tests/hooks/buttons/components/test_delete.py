from model_admin.hooks.buttons.components import DeleteButton
from model_admin.hooks.buttons.entity.button import ButtonEntity
from model_admin.hooks.buttons.helpers.base import BaseButtonHelper
from model_admin.tests.hooks.buttons.test_base.base import TestBaseButtons


class TestBaseHelper(TestBaseButtons):

    def test_validation(self):
        """Should return true if validation is attended"""
        button_validation = DeleteButton.validate(
            permission_helper=self.permission_helper,
            request=self.request,
            obj=self.obj,
            exclude=[]
        )

        self.assertTrue(button_validation)

    def test_render(self):
        """Should render correctly the button"""
        helper = BaseButtonHelper(self.view, self.request)
        expected_entity = ButtonEntity(
            **{
                "url": '',
                "label": 'Delete',
                "classname": '',
                "title": 'Delete this Helper'
            }
        )

        button = DeleteButton().render(
            helper,
            "DELETE",
            [],
            [],
        )
        print(button.to_dict())