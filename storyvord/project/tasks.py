from celery import shared_task
from django.forms import ValidationError
from .models import ProjectAISuggestions, ProjectDetails, ProjectRequirements, ShootingDetails
from .utils import generate_interconnected_report, generate_supplier_recommendations, project_ai_suggestion, generate_report
import time
import requests

REPORT_FLOW = [
    "culture",
    "compliance",
    "logistics", 
    "sustainability",
    "budget"
]

@shared_task(bind=True, max_retries=5)
def process_suggestions_and_reports(self,project_id, regenerate=None):
    try:
        # Fetch the project and related data
        project = ProjectDetails.objects.get(project_id=project_id)
        requirements = ProjectRequirements.objects.get(project=project)
        # shooting_details = ShootingDetails.objects.filter(project=project).values()
        shooting_details = ShootingDetails.objects.filter(project=project)
        shooting_locations = [
            f"{sd.location} ({sd.start_date} to {sd.end_date})" 
            for sd in shooting_details
        ]
        project_details = project.brief
        
        ai_suggestion, created = ProjectAISuggestions.objects.get_or_create(project=project)
                
        # Generate or regenerate reports
        reports = {}
        report_types = [ "crew", "culture", "compliance", "logistics", "sustainability", "suppliers", "budget"]
        for rtype in report_types:
            if not regenerate or rtype in regenerate:
                if rtype == "crew":
                    reports[rtype] = project_ai_suggestion(project, requirements, shooting_details)
                elif rtype == "suppliers":
                    reports[rtype] = generate_supplier_recommendations(project_details, requirements, shooting_locations)
                else:
                    reports[rtype] = generate_interconnected_report(rtype, project, requirements, shooting_locations)
                    # reports[rtype] = generate_report(rtype, project_details, shooting_details)
                    
        update_fields = {}
        if "logistics" in reports:
            update_fields['suggested_logistics'] = reports["logistics"]
        if "budget" in reports:
            update_fields['suggested_budget'] = reports["budget"]
        if "compliance" in reports:
            update_fields['suggested_compliance'] = reports["compliance"]
        if "culture" in reports:
            update_fields['suggested_culture'] = reports["culture"]
        if "crew" in reports:
            update_fields['suggested_crew'] = reports["crew"]
        if "sustainability" in reports:
            update_fields['sustainability_report'] = reports["sustainability"]
        if "suppliers" in reports:
            update_fields['recommended_suppliers'] = reports["suppliers"]
        
        if update_fields:
            for field, value in update_fields.items():
                setattr(ai_suggestion, field, value)
            ai_suggestion.save(update_fields=update_fields.keys())

        return {
            'success': True,
            'updated_fields': list(update_fields.keys()),
            'ai_suggestion': ai_suggestion.id 
        }
    except requests.exceptions.RequestException as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except Exception as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

def call_with_retry(func, *args, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429:  # Too Many Requests
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    raise Exception("Max retries exceeded")



# utils.py
def validate_budget(project, report_data):
    allocated = sum(float(v['amount']) for v in report_data.values() if 'amount' in v)
    total_budget = float(project.requirements.budget)
    
    if allocated > total_budget * 1.15:
        raise ValidationError("Exceeds 15% budget variance limit")
    
    # Cross-check with logistics costs
    logistics_cost = project.ai_context.get('logistics', {}).get('transport_cost', 0)
    if report_data['transport'] < logistics_cost * 0.9:
        raise ValidationError("Transport budget mismatch with logistics plan")