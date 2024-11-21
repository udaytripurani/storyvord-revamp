from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ai_assistant.serializers import ProjectRequirementsSerializer
from project.models import ProjectRequirements
from crew.models import CrewProfile
from accounts.models import PersonalInfo
from pydantic import BaseModel
from typing import List
from openai import OpenAI

client = OpenAI()

class Requirement(APIView):
    """
    APIView to handle project requirements and provide AI-generated crew and equipment suggestions.
    """
    serializer_class = ProjectRequirementsSerializer

    def post(self, request):
        req_id = request.query_params.get('req_id')
        try:
            # Fetching project requirements
            project_requirement = ProjectRequirements.objects.get(id=req_id)
            project = project_requirement.project
            crew_titles = project_requirement.crew_requirements.values_list('crew_title', flat=True)
            equipment_titles = project_requirement.equipment_requirements.values_list('equipment_title', flat=True)
        except ProjectRequirements.DoesNotExist:
            return Response({"message": "No project requirement found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Filtering crew members based on job titles
        crew_filter = Q()
        for title in crew_titles:
            crew_filter |= Q(job_title__icontains=title)

        try:
            # Use a recommendation engine to score and filter crew members
            all_crew = PersonalInfo.objects.filter(
                crew_filter
            ).select_related('user', 'crew_profile').distinct()
            
            # Assume we have a function `score_crew` that scores each crew member
            scored_crew = [(crew, self.score_crew(crew, project , crew_titles)) for crew in all_crew]
            
            # Sort by score in descending order
            scored_crew.sort(key=lambda x: x[1], reverse=True)
            
            # Select top 10 to 20 recommended crew members
            recommended_crew = [crew for crew, score in scored_crew[:20]]
            suggested_crew = recommended_crew[:10] if len(recommended_crew) < 20 else recommended_crew
        except Exception as e:
            return Response({"message": "Error occurred while filtering crew.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize crew data
        try:
            crew_data = [
                {
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
                }
                for crew in suggested_crew
            ]
        except Exception as e:
            return Response({"message": "Error occurred while serializing crew data.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Define Pydantic response models
        class CrewData(BaseModel):
            id: str
            name: str
            job_title: str
            bio: str
            location: str
            languages: str
            contact_number: str
            experience: str
            skills: str
            specializations: str
            standardRate: str
            technicalProficiencies: str

        class CrewSuggestionsResponse(BaseModel):
            crew_suggestion: List[CrewData]
            message: str

        class EquipmentData(BaseModel):
            id: str
            name: str
            description: str
            location: str
            rental_rate: str
            availability: str
            features: str

        class EquipmentSuggestionsResponse(BaseModel):
            equipment_suggestions: List[EquipmentData]
            message: str

        # Generate suggestions using OpenAI
        try:
            crew_completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an AI expert providing crew suggestions based on project requirements."},
                    {"role": "user", "content": f"Provide a list of 3-4 crew members based on the project requirements. "
                                                f"Project description: {project.brief}. "
                                                f"Project requirement: {project_requirement}. "
                                                f"Data: {crew_data}"}
                ],
                response_format=CrewSuggestionsResponse,
            )

            equipment_completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an AI expert providing equipment suggestions based on project requirements."},
                    {"role": "user", "content": f"Provide a list of equipment suggestions based on the project requirements. "
                                                f"Project description: {project.brief}. "
                                                f"Equipment requirements: {equipment_titles}."}
                ],
                response_format=EquipmentSuggestionsResponse,
            )

            suggested_crew = self.structured_crew_output(crew_completion.choices[0].message.parsed)
            suggested_equipment = self.structured_equipment_output(equipment_completion.choices[0].message.parsed)

            data = {
                'crew_data': crew_data,
                'suggested_crew': suggested_crew,
                'suggested_equipment': suggested_equipment
            }

        except Exception as e:
            return Response({"message": "Error occurred while generating suggestions.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Suggestions retrieved successfully.",
            "data": data,
        }, status=status.HTTP_200_OK)

    def structured_crew_output(self, parsed_response):
        """
        Convert the parsed crew response into a structured dictionary.
        """
        try:
            return {
                "message": parsed_response.message,
                "data": [item.dict() for item in parsed_response.crew_suggestion],
            }
        except Exception as e:
            raise ValueError(f"Error while parsing crew response: {str(e)}")

    def structured_equipment_output(self, parsed_response):
        """
        Convert the parsed equipment response into a structured dictionary.
        """
        try:
            return {
                "message": parsed_response.message,
                "data": [item.dict() for item in parsed_response.equipment_suggestions]
            }
        except Exception as e:
            raise ValueError(f"Error while parsing equipment response: {str(e)}")
        
    def score_crew(self,crew_member, project,crew_titles):
        """
        Calculate a score for a crew member based on their match with project requirements.
        """
        score = 0
        
        try:
            experience_years = int(crew_member.crew_profile.experience.split(' ')[0])
            if experience_years > 10:
                score += 1
        except ValueError:
            pass
        
        if crew_member.job_title.lower() in [t.lower() for t in crew_titles]:
            score += 1
        else:
            matching_words = [word for word in crew_member.job_title.lower().split() if word in [t.lower() for t in crew_titles]]
            score += len(matching_words) / len(crew_member.job_title.split())

        # if crew_member.location == project.location:
        #     score += 1

        # if crew_member.job_title == project.job_title:
        #     score += 1

        # if crew_member.languages in project.languages:
        #     score += 1

        # Example: Increment score if the crew member is from the required country
        # if crew_member.country == project.country:
        #     score += 1

        return score


