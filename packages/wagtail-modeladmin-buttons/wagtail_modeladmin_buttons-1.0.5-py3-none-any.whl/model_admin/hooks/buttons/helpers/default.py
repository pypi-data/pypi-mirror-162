from .base import BaseButtonHelper
from ..components import DeleteButton, EditButton, InspectButton, DuplicateButton, AddButton


class DefaultButtonHelper(BaseButtonHelper):

    buttons = [
        EditButton,
        DeleteButton,
        InspectButton,
    ]
