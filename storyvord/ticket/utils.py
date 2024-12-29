import smtplib
import ssl
from django.conf import settings
from django.core.mail import send_mail

def send_email_to_user(user_email, ticket_id):
    """Send an email to the user after a new ticket is created."""

    subject = "Ticket Successfully Created"
    body = f"Hello,\n\nYour ticket with ID {ticket_id} has been successfully created.\n\nThank you!"
    sender_email = settings.EMAIL  # Sender's email from settings
    receiver_email = user_email  # The logged-in user's email
    
    # Print email settings for debugging (be cautious with printing sensitive data like passwords)
    print(f"Sender Email: {sender_email}")
    print(f"Email Password: {settings.EMAIL_PASSWORD}")  # Assuming password is set in settings
    
    # Using SMTP to send the email directly with the email password
    try:
        # Establishing a secure SSL connection with the SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:  # Example using Gmail SMTP
            server.login(sender_email, settings.EMAIL_PASSWORD)  # Login with email and password
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, receiver_email, message)
        
        print(f"Email sent to {receiver_email} successfully!")

    except Exception as e:
        print(f"Error: {e}")


def send_email_to_agent(user_email, ticket_id):
    """Send an email to the user after a new ticket is created."""

    subject = "New Ticket Assigned"
    body = f"Hello,\n\nA new ticket with ID {ticket_id} has been assigned to you.\n\nThank you!"
    sender_email = settings.EMAIL  # Sender's email from settings
    receiver_email = user_email  # The logged-in user's email
    
    # Print email settings for debugging (be cautious with printing sensitive data like passwords)
    print(f"Sender Email: {sender_email}")
    print(f"Email Password: {settings.EMAIL_PASSWORD}")  # Assuming password is set in settings
    
    # Using SMTP to send the email directly with the email password
    try:
        # Establishing a secure SSL connection with the SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:  # Example using Gmail SMTP
            server.login(sender_email, settings.EMAIL_PASSWORD)  # Login with email and password
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, receiver_email, message)
        
        print(f"Email sent to {receiver_email} successfully!")

    except Exception as e:
        print(f"Error: {e}")



def send_ticket_update_to_user(user_email, ticket_id, new_status=None, comment_text=None):
    """Send an email to the user when their ticket's status is updated, or a comment is added."""
    
    if new_status and comment_text:
        subject = f"Ticket {ticket_id} - Status Update and New Comment"
        body = f"Hello,\n\nThe status of your ticket with ID {ticket_id} has been updated to: {new_status}.\n\nA new comment has been added: \n{comment_text}\n\nThank you!"
    elif new_status:
        subject = f"Ticket {ticket_id} - Status Update"
        body = f"Hello,\n\nThe status of your ticket with ID {ticket_id} has been updated to: {new_status}.\n\nThank you!"
    elif comment_text:
        subject = f"Ticket {ticket_id} - New Comment Added"
        body = f"Hello,\n\nA new comment has been added to your ticket with ID {ticket_id}:\n\n{comment_text}\n\nThank you!"
    else:
        # If neither status nor comment is passed, we shouldn't send an email
        return
    
    sender_email = settings.EMAIL  # Sender's email from settings
    receiver_email = user_email  # The logged-in user's email
    
    # Print email settings for debugging (be cautious with printing sensitive data like passwords)
    print(f"Sender Email: {sender_email}")
    print(f"Email Password: {settings.EMAIL_PASSWORD}")  # Assuming password is set in settings
    
    # Using SMTP to send the email directly with the email password
    try:
        # Establishing a secure SSL connection with the SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:  # Example using Gmail SMTP
            server.login(sender_email, settings.EMAIL_PASSWORD)  # Login with email and password
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, receiver_email, message)
        
        print(f"Email sent to {receiver_email} successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")



# import logging
# from django.core.mail import send_mail
# from django.conf import settings

# logger = logging.getLogger(__name__)

# def send_email_to_agent(agent_email, ticket_id):
#     """
#     Send an email to the agent when a ticket is assigned to them.
#     """
#     subject = "New Ticket Assigned"
#     body = f"Hello,\n\nA new ticket with ID {ticket_id} has been assigned to you.\n\nThank you!"
#     sender_email = settings.EMAIL  # Ensure this is set in your settings file

#     try:
#         send_mail(
#             subject,
#             body,
#             sender_email,
#             [agent_email],
#             fail_silently=False,
#         )
#         logger.info(f"Email sent to agent {agent_email} for ticket {ticket_id}.")
#     except Exception as e:
#         logger.error(f"Failed to send email to agent {agent_email}: {e}")
