from celery import shared_task
from .models import ProjectAISuggestions, ProjectDetails, ProjectRequirements, ShootingDetails
from .utils import project_ai_suggestion, generate_report


@shared_task
def process_suggestions_and_reports(project_id, regenerate=None):
    try:
        # Fetch the project and related data
        project = ProjectDetails.objects.get(project_id=project_id)
        requirements = ProjectRequirements.objects.get(project=project)
        shooting_details = ShootingDetails.objects.filter(project=project).values()
        project_details = project.brief
        
        # Generate or regenerate reports
        reports = {}
        if not regenerate or "crew" in regenerate:
            reports["ai_suggestion"] = project_ai_suggestion(project, requirements, shooting_details)
        if not regenerate or "logistics" in regenerate:
            reports["logistics"] = generate_report("logistics", project_details, shooting_details)
        if not regenerate or "budget" in regenerate:
            reports["budget"] = generate_report("budget", project_details, shooting_details)
        if not regenerate or "compliance" in regenerate:
            reports["compliance"] = generate_report("compliance", project_details, shooting_details)
        if not regenerate or "culture" in regenerate:
            reports["culture"] = generate_report("culture", project_details, shooting_details)
            
        # Update AI suggestions in the database
        ProjectAISuggestions.objects.update_or_create(
            project=project,
            defaults={
                'suggested_logistics': reports.get("logistics", ""),
                'suggested_budget': reports.get("budget", ""),
                'suggested_compliance': reports.get("compliance", ""),
                'suggested_culture': reports.get("culture", ""),
                'suggested_crew': reports.get("ai_suggestion", "")
            }
        )

        return {
            'success': True,
            'reports': reports
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
