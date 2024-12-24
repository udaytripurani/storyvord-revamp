# models.py

from django.db import models
from django.conf import settings

# The Connection model will track connection requests between users
class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model #TODO Use the User Model instead of AuthUser
        related_name="sent_requests",
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        related_name="received_requests",
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('requester', 'receiver')

    def __str__(self):
        return f"{self.requester.email} -> {self.receiver.email} ({self.status})"

# The ActiveConnection model will store active connections between users
class ActiveConnection(models.Model):
    user_id_1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        related_name="active_connections_1",
        on_delete=models.CASCADE
    )
    user_id_2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        related_name="active_connections_2",
        on_delete=models.CASCADE
    )
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id_1', 'user_id_2')

    def __str__(self):
        return f"Connection between {self.user_id_1.email} and {self.user_id_2.email} at {self.connected_at}"
