from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

# Custom Manager for Agent model
class AgentManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        agent = self.model(email=email, **extra_fields)
        agent.set_password(password)  # Set the password using the Django method
        agent.save(using=self._db)
        return agent

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Custom User model for Agent (inherits from AbstractBaseUser and PermissionsMixin)
class Agent(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Admin purposes
    created_at = models.DateTimeField(auto_now_add=True)

    # Add related_name arguments to avoid conflicts with User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='agents',  # Change reverse relationship name to 'agents'
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='agent_permissions',  # Change reverse relationship name to 'agent_permissions'
        blank=True,
        help_text='Specific permissions for this agent.',
        verbose_name='user permissions',
    )

    objects = AgentManager()

    USERNAME_FIELD = 'email'  # Email will be the username field
    REQUIRED_FIELDS = ['name']  # Fields required when creating a user (besides email)

    def __str__(self):
        return self.email


# Ticket model
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tickets')  
    assigned_to = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')  # Link to Agent
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            today = timezone.localdate()
            date_part = today.strftime('%Y%m%d')
            unique_id = uuid.uuid4().int
            self.ticket_id = f"TCK-{date_part}-{unique_id % 10000:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.title}"

# Comment model
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Agent, on_delete=models.CASCADE)  # Change this to reference 'Agent'
    comment_text = models.TextField()
    visibility = models.CharField(max_length=10, default='public')  # 'public' or 'internal'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on Ticket {self.ticket.ticket_id}"  # Or use any other agent property

