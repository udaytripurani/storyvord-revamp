import logging
import os
from openai import OpenAI  # Example Microsoft OpenAI client SDK (replace with actual SDK or API calls)
# from other_ai_agent import OtherAIAgent  # Example for backup AI agent

logger = logging.getLogger(__name__)

from openai import AzureOpenAI

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-08-01-preview",
)

class AIService:
    def __init__(self):
        """
        Initialize the AIService with primary and optional backup AI agents.
        """
        try:
            self.primary_agent =AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=subscription_key,
                api_version="2024-08-01-preview",
            )
            logger.info("Primary AI agent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize primary AI agent: {e}")
            self.primary_agent = None


        # Uncomment and configure a backup AI agent if needed
        # try:
        #     self.backup_agent = OtherAIAgent(api_key=os.getenv("BACKUP_AI_KEY"))
        #     logger.info("Backup AI agent initialized successfully.")
        # except Exception as e:
        #     logger.warning(f"Failed to initialize backup AI agent: {e}")
        #     self.backup_agent = None

    def _use_backup(self):
        """
        Switch to backup agent if the primary agent fails.
        """
        if hasattr(self, "backup_agent") and self.backup_agent:
            logger.warning("Switching to backup AI agent.")
            return self.backup_agent
        else:
            logger.error("No backup AI agent is configured or available.")
            raise Exception("Backup AI agent is not available.")

    def get_script_suggestions(self, script_content):
        """
        Analyze the script and provide suggestions.
        """
        try:
            response = self.analyze_script(script_content)
            return response.get("suggestions", [])
        except Exception as e:
            logger.error(f"Primary agent failed to analyze script: {e}")
            try:
                return self._use_backup().analyze_script(script_content).get("suggestions", [])
            except Exception as backup_error:
                logger.error(f"Backup agent also failed: {backup_error}")
                raise Exception("Both primary and backup agents failed to provide suggestions.")

    def accept_suggestion(self, script, suggestion_id):
        """
        Accept an AI-generated suggestion and update the script.
        """
        try:
            suggestion = script.suggestions.get(id=suggestion_id)
            script.content = suggestion.updated_content
            script.save()
            return {"message": "Suggestion accepted and script updated."}
        except Exception as e:
            logger.error(f"Error accepting suggestion: {e}")
            raise

    def reject_suggestion(self, script, suggestion_id):
        """
        Reject an AI-generated suggestion.
        """
        try:
            suggestion = script.suggestions.get(id=suggestion_id)
            suggestion.rejected = True
            suggestion.save()
            return {"message": "Suggestion rejected."}
        except Exception as e:
            logger.error(f"Error rejecting suggestion: {e}")
            raise

    def generate_scenes(self, script_content):
        """
        Generate scenes from the script content.
        """
        try:
            response = self.primary_agent.generate_scenes(script_content)
            return response.get("scenes", [])
        except Exception as e:
            logger.error(f"Primary agent failed to generate scenes: {e}")
            try:
                return self._use_backup().generate_scenes(script_content).get("scenes", [])
            except Exception as backup_error:
                logger.error(f"Backup agent also failed to generate scenes: {backup_error}")
                raise Exception("Both primary and backup agents failed to generate scenes.")

    def regenerate_scene(self, scene):
        """
        Regenerate a scene's description or structure.
        """
        try:
            response = self.primary_agent.regenerate_scene(scene.description)
            return response.get("scene", {})
        except Exception as e:
            logger.error(f"Primary agent failed to regenerate scene: {e}")
            try:
                return self._use_backup().regenerate_scene(scene.description).get("scene", {})
            except Exception as backup_error:
                logger.error(f"Backup agent also failed to regenerate scene: {backup_error}")
                raise Exception("Both primary and backup agents failed to regenerate scene.")

    def generate_shots(self, scene_description):
        """
        Generate shots for a given scene description.
        """
        try:
            response = self.primary_agent.generate_shots(scene_description)
            return response.get("shots", [])
        except Exception as e:
            logger.error(f"Primary agent failed to generate shots: {e}")
            try:
                return self._use_backup().generate_shots(scene_description).get("shots", [])
            except Exception as backup_error:
                logger.error(f"Backup agent also failed to generate shots: {backup_error}")
                raise Exception("Both primary and backup agents failed to generate shots.")

    def generate_storyboards(self, scenes):
        """
        Generate storyboards for the given scenes.
        """
        try:
            response = self.primary_agent.generate_storyboards(scenes)
            return response.get("storyboards", [])
        except Exception as e:
            logger.error(f"Primary agent failed to generate storyboards: {e}")
            try:
                return self._use_backup().generate_storyboards(scenes).get("storyboards", [])
            except Exception as backup_error:
                logger.error(f"Backup agent also failed to generate storyboards: {backup_error}")
                raise Exception("Both primary and backup agents failed to generate storyboards.")
    
    def analyze_script(self, script_content):
        """
        Analyze a script to provide suggestions using an AI model.
        """
        try:
            # Define the prompt for the AI model
            prompt = f"""
            Analyze the following script and provide improvement suggestions:
            Script:
            {script_content}
            
            Suggestions:
            1.
            """

            # Make an API call (e.g., OpenAI)
            response = self.primary_agent.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a scriptwriting assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            suggestions = response.choices[0].message.content

            # Parse and return the suggestions
            # suggestions = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"suggestions": suggestions.split("\n")}  # Split suggestions into a list
        except Exception as e:
            logger.error(f"Failed to analyze script: {e}")
            raise

    def generate_scenes(self, script_content):
        """
        Generate scenes from a script using an AI model.
        """
        try:
            # Define the prompt
            prompt = f"""
            Break the following script into individual scenes. Provide a brief description for each scene:
            Script:
            {script_content}

            Scenes:
            1.
            """

            # Make the API call
            response = self.primary_agent.chat_completion(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a screenplay expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            # Parse and return the scenes
            scenes = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"scenes": scenes.split("\n")}  # Split scenes into a list
        except Exception as e:
            logger.error(f"Failed to generate scenes: {e}")
            raise

