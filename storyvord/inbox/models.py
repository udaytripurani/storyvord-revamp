from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel, SoftDeletableManager
from typing import Optional, Any
from django.db.models import Q
from accounts.models import User

class RoomModel(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name=_("Id"))
    name = models.CharField(max_length=255, verbose_name=_("Room Name"))
    members = models.ManyToManyField(User, related_name='rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DialogsModel(TimeStampedModel):
    id = models.BigAutoField(primary_key=True, verbose_name=_("Id"))
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dialogs_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dialogs_as_user2')

    class Meta:
        unique_together = (('user1', 'user2'), ('user2', 'user1'))
        verbose_name = _("Dialog")
        verbose_name_plural = _("Dialogs")

    def __str__(self):
        return _("Dialog between ") + f"{self.user1_id}, {self.user2_id}"
    
    @staticmethod
    def dialog_exists(user1: User, user2: User):
        return DialogsModel.objects.filter(Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)).first()

    @staticmethod
    def create_if_not_exists(user1: User, user2: User):
        if not DialogsModel.dialog_exists(user1, user2):
            DialogsModel.objects.create(user1=min(user1, user2, key=lambda x: x.id),
                                        user2=max(user1, user2, key=lambda x: x.id))

    @staticmethod
    def get_dialogs_for_user(user: User):
        return DialogsModel.objects.filter(Q(user1=user) | Q(user2=user)).select_related('user1', 'user2')

class MessageModel(TimeStampedModel, SoftDeletableModel):
    id = models.BigAutoField(primary_key=True, verbose_name=_("Id"))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    room = models.ForeignKey(RoomModel, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(verbose_name=_("Text"))
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id} from {self.sender} to {self.recipient}"
    
    def save(self, *args, **kwargs):
        # Only create a dialog for user-to-user messages
        if self.recipient:
            DialogsModel.create_if_not_exists(self.sender, self.recipient)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created',)