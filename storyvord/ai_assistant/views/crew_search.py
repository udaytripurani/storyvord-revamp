from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ai_assistant.serializers import ProjectRequirementsSerializer
from project.models import ProjectRequirements , ProjectEquipmentRequirement
from crew.models import CrewProfile
from django.db.models import Q
from accounts.models import PersonalInfo
from pydantic import BaseModel
from typing import List, Dict
from openai import OpenAI
client = OpenAI()

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
                
            class CrewData(BaseModel):
                id: str
                name: str
                job_title: str
                bio: str
                location: str
                languages: List[str]
                contact_number: str
                experience: str
                skills: List[str]
                specializations: List[str]
                standardRate: str
                technicalProficiencies: List[str]

            class CrewSuggestionsResponse(BaseModel):
                crew_suggestion: List[CrewData]
                
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an AI expert providing crew suggestions based on project requirements."},
                    {"role": "user", "content": f"Provide a list of 3-4 crew members based on the project requirements. "
                                                f"Project requirement is this: {project_requirement}. "
                                                f"Give the suggestion in JSON format from this data: {crew_data}"}
                ],
                 response_format=CrewSuggestionsResponse,
            )
            
            ai_response = completion.choices[0].message.parsed

            data = {
                'AI Suggestion': ai_response,
                'crew_data': crew_data
            }
            
        except Exception as e:
            return Response({"message": "Error occurred while serializing results.","error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Crew suggestions retrieved successfully.",
            "data": data,
        }, status=status.HTTP_200_OK)
