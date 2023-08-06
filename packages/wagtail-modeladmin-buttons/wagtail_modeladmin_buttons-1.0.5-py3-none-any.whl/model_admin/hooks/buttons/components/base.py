from typing import List, Type
from model_admin.hooks.buttons.entity.button import ButtonEntity


class Button:
    """Every button to display on listing objects in wagtail

    Attributes:
        default_classnames (List[str]): default classes for every button. By default, all buttons need to have the
        "button" class
        custom_classnames (List[str]): As needed, you must pass the custom classes for the button in this attribute
    """
    default_classnames: List[str] = ["button"]
    custom_classnames: List[str] = []

    @staticmethod
    def validate(permission_helper: "PermissionHelper", request: "WSGIRequest", obj: "Model", exclude: list) -> bool:
        """Validate a conditional before rendering

        Args:
            permission_helper (PermissionHelper): Permission class passed in wagtail_hooks
            request (WSGIRequest): The request containing all data about user and so on
            obj (Model): Instance of any django model
            exclude (list): a list of string to exclude for the verification

        Returns:
            bool: If true, the user has permission to do the action
        """
        return True

    def _get_classnames(self, classnames_add: List[str], classnames_exclude: List[str]) -> str:
        """Make a string containing all css classes

        Args:
            classnames_add (List[str]): A list of css classes to render
            classnames_exclude (List[str]): A list of css classes to exclude from the render

        Returns:
            str: String containing all classes concatenated

        Examples:

            If pass the following data:
            classnames_add = ["class1", "class2", "class3"]
            classnames_exclude = ["class3"]

            The return will be the following:

            print(self._get_classnames(classnames_add, classnames_exclude))
            output: "class1 class2"

        IMPORTANT:
            There's 2 attributes defined in this class:

            - default_classnames
            - custom_classnames

            This method concatenate all passed classes with this 2 attributes.

            Every button may have your customized classes, defined directly in the class
        """
        classnames_add = [] if classnames_add is None else classnames_add
        classnames_exclude = [] if classnames_exclude is None else classnames_exclude
        mixed = self.default_classnames + self.custom_classnames + classnames_add

        final_classes = [cn for cn in mixed if cn not in classnames_exclude]
        return ' '.join(final_classes)

    def render(
            self,
            helper: "Type[BaseButtonHelper]",
            pk: str,
            classnames_add: List[str] = None,
            classnames_exclude: List[str] = None,
            *args,
            **kwargs
    ) -> ButtonEntity:
        """Render a button

        Args:
            helper (Type[BaseButtonHelper]): the helper used to get all the important data of object as: model, current
            instance, view, request and so on
            pk (str): the primary key of current object
            classnames_add (List[str]): A list of css classes to render
            classnames_exclude (List[str]): A list of css classes to exclude from the render

        Returns:
            ButtonEntity: A object containing the following fields:

                url:
                label: str
                classname: str
                title: str
        """
        raise NotImplementedError("You must implement the `_render` method.")
