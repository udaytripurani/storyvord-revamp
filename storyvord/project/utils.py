from project.models import ProjectDetails, ProjectRequirements, ShootingDetails
from pydantic import BaseModel
from typing import List
from openai import OpenAI

from storyvord.exception_handlers import custom_exception_handler
# client = OpenAI()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

import os
import base64
from openai import AzureOpenAI

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from threading import Thread
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-08-01-preview",
)

SUSTAINABILITY_SCHEMA = {
    "type": "object",
    "properties": {
        "carbon_footprint_estimate": {"type": "string"},
        "energy_sources": {"type": "array"},
        "waste_reduction": {"type": "string"},
        "sustainable_transport": {"type": "object"},
        "community_impact": {"type": "string"},
        "cost_impact": {"type": "string"},
        "long_term_benefits": {"type": "string"}
    },
    "required": ["carbon_footprint_estimate", "energy_sources"]
}

SUPPLIER_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z_\\-\\s]+$": {  # city names (e.g. "mumbai")
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "name": {"type": "string"},
                    "pros": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "cons": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "cost_estimate": {"type": "string"},
                    "sustainability_rating": {"type": "number"}
                },
                "required": ["type", "name", "pros", "cons", "cost_estimate", "sustainability_rating"]
            }
        }
    },
    "additionalProperties": False
}

SUPPLIER_PROMPT = """Analyze these project requirements and suggest local suppliers:
    
**Project Details**
- Project Brief: {project_brief}
- Budget: {budget_currency}{budget}
- Locations: {locations}
- Crew Size: {crew_size}
- Equipment Needed: {equipment}
- Shooting Dates: {dates}

**Required Supplier Types**
{required_categories}

**Format Requirements**
- The response must be in valid JSON format.
- Categorize by location and supplier type.
- Include contact info when possible.
- Add 'pros' and 'cons' for each supplier.
- Match to project's sustainability goals.
- Prioritize vendors with film industry experience.

**Example JSON Response Format**
{{
  "mumbai": [
    {{
      "type": "catering",
      "name": "Bollywood Bites",
      "pros": ["Vegetarian options", "Film set experience"],
      "cons": ["Limited gluten-free choices"],
      "cost_estimate": "₹1500/meal",
      "sustainability_rating": 4.2
    }}
  ]
}}"""


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
        
        role_messages = {
            "logistics": "You are an expert logistics coordinator for film productions with 20+ years experience planning complex shoots.",
            "budget": "You are a senior film production accountant specializing in budget optimization for indie and studio films.",
            "compliance": "You are a legal compliance officer specializing in international film production regulations.",
            "culture": "You are a cultural consultant with PhD-level knowledge of global filming locations.",
            "sustainability": "You are a sustainability expert certified in green film production practices.",
            "crew": "You are a veteran line producer with deep connections in global film crew networks.",
            "suppliers": "You are a procurement specialist with expertise in sourcing film production suppliers."
        }
        
        system_role = role_messages.get(report_type, "You are a film production expert.")
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"} if report_type == "sustainability" else None,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        f"{system_role} "
                        "Always provide actionable recommendations. "
                        "Consider both cost efficiency and practical feasibility. "
                        "Highlight potential risks using :warning: emoji."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        if report_type == "sustainability":
            generated_data = json.loads(completion.choices[0].message.content)
            validate(generated_data, SUSTAINABILITY_SCHEMA)
            return generated_data
        
        return completion.choices[0].message.content

    except ValidationError as ve:
        logger.error(f"Schema validation failed: {str(ve)}")
        return {"error": "Invalid sustainability data format"}
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response")
        return {"error": "Invalid JSON format"}
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return {"error": str(e)}
    
# utils.py
def generate_interconnected_report(report_type,project_details, requirements, shooting_locations):
    # Load existing context
    context = project_details.ai_context
    
    # Define report dependencies
    dependencies = {
        "budget": ["logistics", "compliance", "culture", "sustainability"],
        "sustainability": ["logistics", "budget"],
        "logistics": ["culture"],
        "compliance": ["culture"],
        "suppliers": ["logistics"]
    }
    
    # Get required context from other reports
    required_data = {}
    for dep in dependencies.get(report_type, []):
        required_data[dep] = context.get(dep, {})
    
    # Create detailed prompt
    prompt = f"""
    Generate comprehensive {report_type} report for film production with these requirements:
    
    Project Budget: {requirements.budget_currency}{requirements.budget}
    Project Brief: {project_details.brief}
    Shooting Locations:{', '.join(shooting_locations)}
    
    Related Report Data:
    {json.dumps(required_data, indent=2)}
    
    Required Sections:
    - Executive Summary
    - Cost Breakdown (with percentage of total budget)
    - Timeline Impact Analysis
    - Risk Assessment
    - Location-Specific Considerations
    - Synergy with Other Departments
    - Long-Term Benefits
    
    Format requirements:
    - Use markdown with header levels ## for sections, ### for subsections
    - Include tables for cost comparisons
    - Use :warning: emoji for critical risks
    - Reference related report data where applicable
    """
    
    # Generate report
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"You are a {report_type} expert. Use exact numbers from project budget: {requirements.budget}"
            },
            {"role": "user", "content": prompt}
        ]
    )
    
    # Update context
    context[report_type] = completion.choices[0].message.content
    project_details.ai_context = context
    project_details.save()
    
    return completion.choices[0].message.content

def generate_supplier_recommendations(project, requirements, locations):
    
    # Get equipment needs
    equipment = [
        req.equipment_title for req in 
        requirements.equipment_requirements.all()
    ]
    
    prompt = SUPPLIER_PROMPT.format(
        project_brief=project,
        budget_currency=requirements.budget_currency,
        budget=requirements.budget,
        locations=", ".join(locations),
        crew_size=requirements.crew_requirements.count(),
        equipment=", ".join(equipment),
        dates=", ".join(locations),
        required_categories="\n".join([
            "- Camera equipment rentals",
            "- Catering services", 
            "- Transportation providers",
            "- Location permits"
            '- Use city names in CamelCase format (e.g., "NewYork", "LosAngeles", "HongKong").'
        ])
    )
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a local vendor expert with knowledge of film industry suppliers across India."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    generated_data = json.loads(completion.choices[0].message.content)
    try:
        validate(generated_data, SUPPLIER_SCHEMA)
    except Exception as e:
        generated_data = {generated_data}
    return generated_data


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

