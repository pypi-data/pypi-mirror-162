from unittest.mock import Mock

VIEW_MOCK = Mock(
            model=Mock(
                _meta=Mock(
                    pk=Mock(attname="id"),
                    verbose_name="Helper",
                    verbose_name_plural="Helpers",
                )
            ),
            url_helper=Mock(
                create_url="add.url"
            ),
            permission_helper=Mock()
        )
REQUEST_MOCK = Mock()
PERMISSION_HELPER_MOCK = Mock(
    user_can_delete_obj=Mock(return_value=True)
)
OBJECT_MOCK = Mock(id="UUID_QUALQUER")



