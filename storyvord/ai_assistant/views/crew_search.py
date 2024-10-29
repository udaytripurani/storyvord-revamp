from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ai_assistant.serializers import ProjectRequirementsSerializer
from project.models import ProjectRequirements , ProjectEquipmentRequirement
from crew.models import CrewProfile
from django.db.models import Q
from accounts.models import PersonalInfo

class CrewSearch(APIView):
    serializer_class = ProjectRequirementsSerializer

    def post(self, request):
        req_id = request.query_params.get('req_id')
        try:
            project_requirement = ProjectRequirements.objects.get(id=req_id)
            crew_titles = project_requirement.crew_requirements.values_list('crew_title', flat=True)
        except ProjectRequirements.DoesNotExist:
            return Response({"message": "No project requirement found."}, status=status.HTTP_404_NOT_FOUND)
        
        crew_filter = Q()
        for title in crew_titles:
            crew_filter |= Q(job_title__icontains=title)

        try:
            suggested_crew = PersonalInfo.objects.filter(
                crew_filter
            ).select_related('user', 'crew_profile').distinct()
        except CrewProfile.DoesNotExist:
            return Response({"message": "Crew not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Error occurred while filtering crew.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            suggested_equipment = project_requirement.equipment_requirements.all()
        except ProjectEquipmentRequirement.DoesNotExist:
            return Response({"message": "Equipment not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            crew_data = []
            for crew in suggested_crew:
                crew_data.append({
                    "id": crew.user.id,
                    "name": crew.full_name,
                    "job_title": crew.job_title,
                    "bio": crew.bio,
                    "location": crew.location,
                    "languages": crew.languages,
                    "contact_number": crew.contact_number,
                    "experience": crew.crew_profile.experience,
                    "skills": crew.crew_profile.skills,
                    "specializations": crew.crew_profile.specializations,
                    "standardRate": crew.crew_profile.standardRate,
                    "technicalProficiencies": crew.crew_profile.technicalProficiencies
                })
            equipment_data = []
            for equipment in suggested_equipment:
                equipment_data.append({
                    "name": equipment.equipment_title,
                    "quantity": equipment.quantity
                })
            
        except Exception as e:
            return Response({"message": "Error occurred while serializing results.","error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response({
            "crew_suggestions": crew_data,
            "equipment_suggestions": equipment_data
        }, status=status.HTTP_200_OK)
