from typing import Type, List

from django.urls import re_path
from wagtail.contrib.modeladmin.options import ModelAdmin

from model_admin.hooks.buttons.components import Button
from model_admin.hooks.buttons.helpers.default import DefaultButtonHelper
from model_admin.hooks.views.duplicate import DuplicateView


class BaseModelAdmin(ModelAdmin):

    duplicate_view_class = DuplicateView
    duplicate_template_name: str = ''
    add_custom_buttons: List[Type[Button]] = []

    def duplicate_view(self, request, instance_pk):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk}
        view_class = self.duplicate_view_class
        return view_class.as_view(**kwargs)(request)

    def get_duplicate_template(self):
        return self.duplicate_template_name or self.get_templates('duplicate')

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls = urls + (
            re_path(
                self.url_helper.get_action_url_pattern('duplicate'),
                self.duplicate_view,
                name=self.url_helper.get_action_url_name('duplicate')),
        )
        return urls

    def _validate_added_buttons(self) -> bool:
        """Validates if added buttons is a list

        Returns
            True or raise an exception
        """
        if not isinstance(self.add_custom_buttons, list):
            raise Exception("`add_custom_buttons` must be a list of Buttons object (List[Type[Button]])")
        return True

    def _add_custom_buttons(self, button_helper_class):
        """
        Add the custom buttons to button_helper_class

        The `button_helper_class` has a attribute called `buttons` that is a List with buttons to render when listing
        objects in wagtail admin.

        If you wanna to add customized buttons on listing, you just need to add your custom Button on attribute called
        `add_custom_buttons` which is also a List of buttons.

        This attribute, must be defined in the class that inherits from this class (commonly defined in wagtail_hooks).

        Examples:

            @modeladmin_register
            class CompanyAdmin(BaseModelAdmin):
                ...
                add_custom_buttons = [
                    DuplicateButton
                ]

        Args:
            button_helper_class:

        Returns:

        """
        is_valid = self._validate_added_buttons()
        if is_valid:
            for button in self.add_custom_buttons:
                if button not in button_helper_class.buttons:
                    button_helper_class.buttons.append(button)
        return button_helper_class

    def get_button_helper_class(self):
        """
        Returns a ButtonHelper class to help generate buttons for the given
        model.
        """
        button_helper_class = self.button_helper_class if self.button_helper_class else DefaultButtonHelper
        return self._add_custom_buttons(button_helper_class)


