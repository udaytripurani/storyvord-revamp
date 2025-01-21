from project.models import ProjectDetails, ProjectRequirements, ShootingDetails
from pydantic import BaseModel
from typing import List
from openai import OpenAI

from storyvord.exception_handlers import custom_exception_handler
# client = OpenAI()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import os
import base64
from openai import AzureOpenAI

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-08-01-preview",
)

def project_ai_suggestion(project, requirements, shooting_details):
    
    class SuggestedData(BaseModel):
        compliance: List[str]
        logistics: List[str]
        budget: List[str]
        culture: List[str]
    
    class ShootingDetailsData(BaseModel):
        id: str
        location: str
        start_date: str
        end_date: str
        mode_of_shooting: str
        permits: str
        ai_suggestion: List[SuggestedData]

    class ProjectSuggestionsResponse(BaseModel):
        message: str
        ai_suggestions: List[ShootingDetailsData]
            
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "I need you to act as a line producer with expertise in local locations, compliance issues, "
                    "and cultural nuances. You have a strong understanding of the risks involved in film production, "
                    "especially related to location-specific factors. You are also skilled in budgeting for films, "
                    "including compliance costs, and creating detailed itineraries to ensure compliance. Your knowledge "
                    "covers locations worldwide, from big cities to small towns in every country. Given this expertise, "
                    "provide advice using critical thinking based on further details I will provide, such as crew size, "
                    "equipment (like cameras), and the type of shoot (indoor, outdoor, corporate, or blog). Offer two options "
                    "when appropriate. Your response should include a comprehensive overview, and feel free to ask questions to "
                    "better understand my production needs. You need to provide me every single details possible for this project "
                    "like compliance, logistic, budget, and culture. I need at least 10000 words for each."
                )},
                {"role": "user", "content": (
                    f"Provide me the suggestions for the project"
                    f"Project description: {project.brief}."
                    f"Project requirements: {requirements}."
                    f"Shooting details: {shooting_details}."
                )}
            ],
            response_format=ProjectSuggestionsResponse,
        )
        structured_response = structured_crew_output(completion.choices[0].message.parsed)
        return structured_response
    except Exception as e:
        return {"message": "An error occurred while processing your request", "data": []}
 
def structured_crew_output(parsed_response):
        """
        Convert the parsed crew response into a structured dictionary.
        """
        try:
            return {
                "message": parsed_response.message,
                "data": [item.dict() for item in parsed_response.ai_suggestions],
            }
        except Exception as e:
            raise ValueError(f"Error while parsing crew response: {str(e)}")
        
    
def generate_prompt(report_type, project_details, shooting_details):
    prompts = {
        "logistics": f"""
        Given the following project details, generate a comprehensive logistics plan including transportation(Mode of Travel and Price break down),Consider how the crew and equipment will be transported,How far is the shoot location from the shoot location, accommodation, and any relevant recommendations:

        Project Details:
        {project_details}
        Shooting Details:
        {shooting_details}

        Provide the report in markdown format with clear headers and bullet points.
        """,
        "budget": f"""
        Create a detailed budget breakdown for the project described below. Include crew salaries, equipment rentals, transportation, accommodations, compliance, and miscellaneous expenses. Provide clear calculations and a final estimated total.

        Project Details:
        {project_details}
        Shooting Details:
        {shooting_details}

        Provide the report in markdown format with appropriate sections.
        """,
        "compliance": f"""
        Based on the project details provided, outline the compliance requirements for the given location. Include necessary permits, local authority contacts, risk considerations, and recommendations for navigating local regulations.

        Project Details:
        {project_details}
        Shooting Details:
        {shooting_details}

        Provide the response in markdown format, organized into sections.
        """,
        "culture": f"""
        Generate a detailed cultural considerations report for the specified shoot location. Focus on local customs, norms, and any cultural practices that could influence the production. Include recommendations for the crew to adapt and integrate effectively.

        Project Details:
        {project_details}
        Shooting Details:
        {shooting_details}

        Provide the report in markdown format with clear sections.
        """
    }
    return prompts.get(report_type, "Invalid report type.")

@csrf_exempt
def generate_report(report_type,project_details,shooting_details):
    try:
        # Generate the prompt
        prompt = generate_prompt(report_type,project_details,shooting_details)

        if prompt == "Invalid report type.":
            return JsonResponse({"error": "Invalid report type."}, status=400)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"I need you to act as a line producer with expertise in local locations, compliance issues, and cultural nuances. You have a strong understanding of the risks involved in film production, especially related to location-specific factors."
                    f"You are also skilled in budgeting for films, including compliance costs, and creating detailed itineraries to ensure compliance."
                    f"Your knowledge covers locations worldwide, from big cities to small towns in every country."
                    f"Given this expertise, provide advice using critical thinking based on further details I will provide"},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        generated_text = completion.choices[0].message.content

        return generated_text

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from threading import Thread
from django.conf import settings

def send_invitation_email(user, project, role):
    # Render the email body from the template
    email_body = render_to_string('email/invitation.html', {
        'user': user,
        'project': project,
        'role': role,
    })
    
    # Default sender email (can be configured in settings)
    from_email = f"Storyvord Platform <{getattr(settings, 'DEFAULT_FROM_EMAIL', 'DEFAULT_NO_REPLY_EMAIL')}>"

    # Create the email message
    email = EmailMessage(
        subject=f"Invitation to join the project: {project.name}",
        body=email_body,
        from_email=from_email,
        to=[user.email],
    )
    email.content_subtype = 'html'  # Set email content type to HTML

    # Send the email asynchronously using a thread
    EmailThread(email).start()


class EmailThread(Thread):
    def __init__(self, email):
        self.email = email
        Thread.__init__(self)

    def run(self):
        self.email.send()

