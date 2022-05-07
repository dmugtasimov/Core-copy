from functools import partial

from django.db import models
from model_utils import FieldTracker

from core.accounts import consumers
from core.accounts.consumers import MessageType
from core.core.constants import ACCOUNT_NUMBER_LENGTH
from core.core.models import CustomModel
from core.core.utils.misc import apply_on_commit
from core.core.validators import HexStringValidator

from ..constants import DISPLAY_NAME_MAX_LENGTH


class Account(CustomModel):
    account_number = models.CharField(
        max_length=ACCOUNT_NUMBER_LENGTH, validators=(HexStringValidator(ACCOUNT_NUMBER_LENGTH),), primary_key=True
    )
    avatar = models.URLField(blank=True)
    balance = models.PositiveBigIntegerField()
    display_name = models.CharField(blank=True, max_length=DISPLAY_NAME_MAX_LENGTH)

    tracker = FieldTracker()

    def __str__(self):
        return f'{self.account_number} | {self.balance}'

    def save(self, *args, **kwargs):
        if self.tracker.has_changed('balance') or self._state.adding:
            # TODO(dmu) MEDIUM: Consider always send an update notifications, but containing only those fields that
            #                   were updated
            # TODO(dmu) MEDIUM: Consider using serializer to create `message` if it gets more complex
            apply_on_commit(
                # `consumers.send` so we can mock `send` in `consumers`
                partial(consumers.send, MessageType.UPDATE_ACCOUNT, self.account_number, {'balance': self.balance})
            )

        return super().save(*args, **kwargs)
