from re import search
from typing import Type, List

from django.db.models import Model
from django.utils.text import slugify


class DuplicateObject:

    @classmethod
    def _set_copy_to_text(cls, obj: Type[Model], field: str) -> str:
        """Set the string `COPY` to the field.

        Args:
            obj (Model): A Django model
            field (str): The field name that will want to be found

        Returns:
            str: The string with COPY concatenated

        """
        final_text = "COPY %s" % getattr(obj, field)
        if search("slug", field):
            final_text = slugify(final_text)
        return final_text

    @classmethod
    def _auto_import_unique_fields(cls, obj: Type[Model]) -> List[str]:
        """Auto retrieve all unique fields defined in model

        Args:
            obj (Model): A Django model

        Returns:
            List[str]: A list with all fields to modify
        """
        fields = []
        for field in obj._meta.get_fields():  # noqa
            if hasattr(field, "unique") and field.unique:
                if "id" not in field.name:
                    fields.append(field.name)
        return fields

    @classmethod
    def _remove_duplicates(cls, lists: List[List[str]]) -> List[str]:
        """Auto retrieve all unique fields defined in model

        Args:
            lists (List[List[str]]): A list of lists with all fields to create a only one list

        Returns:
            List[str]: A list containing all fields (without duplicates)
        """
        all_lists = []
        for li in lists:
            all_lists = all_lists + li
        return list(set(all_lists))

    @classmethod
    def _get_fields(cls, obj: Type[Model]) -> List[str]:
        """Get all fields to concatenate the text COPY.

        Args:
            obj (Model): A Django model

        Returns
        """
        unique_fields = cls._auto_import_unique_fields(obj)

        if hasattr(obj, "UNIQUE_FIELDS_TO_DUPLICATE"):
            unique_fields = cls._remove_duplicates([
                unique_fields,
                obj.UNIQUE_FIELDS_TO_DUPLICATE,
            ])
        return unique_fields

    @classmethod
    def do(cls, obj: Type[Model]) -> None:
        obj.pk = None
        for field in cls._get_fields(obj):
            setattr(obj, field, cls._set_copy_to_text(obj, field))
        obj.save()
