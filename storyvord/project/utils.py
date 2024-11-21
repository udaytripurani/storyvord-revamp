from project.models import ProjectDetails
from pydantic import BaseModel
from typing import List
from openai import OpenAI
client = OpenAI()

def project_ai_suggestion(project_id):
    project = ProjectDetails.objects.get(project_id=project_id)
    
    class SuggestedData(BaseModel):
        compliance: str
        logictics: str
        budget: str
        culture: str

    class ProjectSuggestionsResponse(BaseModel):
        ai_suggestions: List[SuggestedData]
        message: str
            
    try:
        completion = client.beta.chat.completions.parse(
                    model="gpt-4o-2024-08-06",
                    messages=[
                        {"role": "system", "content": "I need you to act as a line producer with expertise in local locations, compliance issues, and cultural nuances. You have a strong understanding of the risks involved in film production, especially related to location-specific factors. You are also skilled in budgeting for films, including compliance costs, and creating detailed itineraries to ensure compliance. Your knowledge covers locations worldwide, from big cities to small towns in every country. Given this expertise, provide advice using critical thinking based on further details I will provide, such as crew size, equipment (like cameras), and the type of shoot (indoor, outdoor, corporate, or blog). Offer two options when appropriate. Your response should include a comprehensive overview, and feel free to ask questions to better understand my production needs."},
                        {"role": "user", "content": f"Provide me the suggestions for the project"
                                                    f"Project description: {project.brief}. "
                                                    }
                    ],
                    response_format=ProjectSuggestionsResponse,
                )

        suggestion = structured_crew_output(completion.choices[0].message.parsed)
        return suggestion
    except Exception as e:
        print(f"Error : {e}")
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