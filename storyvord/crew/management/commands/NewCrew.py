import json
import os
import django
import random
import requests
from django.core.files.base import ContentFile
from accounts.models import User, PersonalInfo, Country, UserType
from crew.models import CrewProfile

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storyvord.settings")  
django.setup()


# Load the JSON data from a file
json_file_path = 'crew/management/commands/formattedCrewData-2.json'  
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

def truncate(value, max_length):
    return value[:max_length] if value else None

# List jobtile, experience, skills, technicalProficiencies, specializations 
film_crew_roles = [
    "Producer",
    "Executive Producer",
    "Director",
    "Line Producer",
    "Production Manager",
    "Director of Photography (DP)",
    "First Assistant Director (1st AD)",
    "Script Supervisor",
    "Camera Operator",
    "Gaffer",
    "Production Designer",
    "Editor",
    "Sound Designer",
    "Casting Director",
    "Stunt Coordinator"
]

def random_role():
    return random.choice(film_crew_roles)

# Function to load country data
def load_country(data):
    

    try:
        country, created = Country.objects.get_or_create(
            name = data.get('countryName'),
            defaults={
                'alpha_2_code': data.get('countryShort'),
                # 'alpha_3_code': data.get('countryShort'),
            }
        )
        if created:
            print(f"Created Country: {country.name}")
        else:
            print(f"Country already exists: {country.name}")
        
        return country

    except Country.DoesNotExist:
        print("Country not found, creating new one...")
        # Fallback if you want to create a new country without the code issue
        # Just for testing purpose
        country = Country.objects.create(
            name=data.get('countryName'),
            alpha_2_code=data.get('countryShort'),
            alpha_3_code=data.get('countryShort'),
        )
        print(f"Created new Country: {country.name}")
        return country
    except Exception as e:
        print(f"An error occurred: {e}")



# -- Doesnt Upload on Azure Blob Storage --
# ----------------------------------------
# def helper_user_image(data):
#     image_url = data.get("image", {}).get("transforms", {}).get("profile128")
#     if image_url:
#         # Download the image content
#         img_response = requests.get(image_url)
#         img_name = image_url.split("/")[-1]  
#         image = ContentFile(img_response.content, name=img_name)
#     else:
#         image = None 
#     return image


# Function to load user and personal info data
def load_user(data):
    usertype = UserType.objects.get(name="crew")
    role = random_role()

    user, created = User.objects.get_or_create(
        email=data.get("slug") + "@example.com",  
        defaults={
            "is_active": True,
            "verified": True,
            "user_type": usertype, 
            "steps": True,
        }
    )
    
    # Create or update PersonalInfo data
    PersonalInfo.objects.update_or_create(
        user=user,
        defaults={
            "full_name": truncate(f"{data.get('firstName')} {data.get('lastName')}", 256),
            "bio": data.get("description"),
            "location": truncate(data.get("location", {}).get("formattedAddress"), 256),
            "contact_number": truncate("N/A", 256),
            "job_title": role,
            "image": data.get("image", {}).get("transforms", {}).get("profile128"),
            "languages": "English",
            # "image": helper_user_image(data),
        }
    )
    print(f"{'Created' if created else 'Updated'} User: {user.email}")

    # Create or update CrewProfile with additional data
    crew_profile, created_crew_profile = CrewProfile.objects.update_or_create(
        user=user,
        defaults={
            "personal_info": user.personalinfo,

            # "experience": 
            # "skills": 
            # "technicalProficiencies": 
            # "specializations":
            "experience": role,
            "skills": role,
            "technicalProficiencies": role,
            "specializations": role,

            # Avg of minRate and maxRate
            "standardRate": (data.get("profile", {}).get("maxRate") + data.get("profile", {}).get("minRate")) / 2,
            "drive": True,
            "active": True,
        }
    )
    
    return user



# Main function to load all data
def load_data():
    for user_data in data:


        # get or create country
        country_data = user_data.get("location", {})
        if country_data:
            country = load_country(country_data)
        
        user = load_user(user_data)
        
        # Load project digests for the user
        # if "projectDigests" in user_data:
            # load_project_digests(user, user_data["projectDigests"])

# Run the data loading process
load_data()
print("Data loading completed.")