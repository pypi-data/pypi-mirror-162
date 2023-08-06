from django.test import TestCase

from model_admin.tests.hooks.buttons.test_base.mocks import (
    VIEW_MOCK,
    REQUEST_MOCK,
    PERMISSION_HELPER_MOCK, OBJECT_MOCK
)


class TestBaseButtons(TestCase):

    def setUp(self) -> None:
        self.view = VIEW_MOCK
        self.request = REQUEST_MOCK
        self.permission_helper = PERMISSION_HELPER_MOCK
        self.obj = OBJECT_MOCK
