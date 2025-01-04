
#TODO
# GET /api/scripts/{id}/: Fetch script content as text or download as a file.
# POST /api/scripts/upload/: Upload a script as text or file.
# PUT /api/scripts/{id}/: Update the script content.

# POST /api/scripts/{id}/suggestions/: Fetch AI-based suggestions for the script.
# PUT /api/scripts/{id}/suggestions/{suggestion_id}/accept/: Accept AI suggestions.
# PUT /api/scripts/{id}/suggestions/{suggestion_id}/reject/: Reject AI suggestions.

# POST /api/scripts/{id}/scenes/: Generate scenes from a script.
# PUT /api/scenes/{scene_id}/: Edit scene description or order.
# DELETE /api/scenes/{scene_id}/: Delete a scene.
# POST /api/scenes/{scene_id}/regenerate/: Regenerate AI suggestions for a scene.

# POST /api/scenes/{scene_id}/shots/: Generate shots for a scene.
# PUT /api/shots/{shot_id}/done/: Mark a shot as done.

# PUT /api/scenes/{scene_id}/timeline/: Save or update the timeline for a scene and its shots.

# POST /api/sequences/: Create a sequence from finalized scenes and shots.

# POST /api/storyboards/: Generate a storyboard for each scene and its shots.

# PUT /api/storyboards/{id}/: Edit storyboard details or replace images.


from django.urls import path
from .views import (
    ScriptListView,
    ScriptDetailView,
    ScriptUploadView,
    ScriptUpdateView,
    ScriptDeleteView,
    ScriptSuggestionView,
    ScriptSuggestionActionView,
    CreateSceneView,
    GenerateScenesView,
    EditSceneView,
    DeleteSceneView,
    RegenerateSceneView,
    GenerateShotsView,
    MarkShotDoneView,
    UpdateTimelineView,
    CreateSequenceView,
    GenerateStoryboardView,
    EditStoryboardView,
)

urlpatterns = [
    # Script endpoints
    path('scripts/', ScriptListView.as_view(), name='script-list'),
    path('scripts/<int:id>/', ScriptDetailView.as_view(), name='script-detail'),
    path('scripts/upload/', ScriptUploadView.as_view(), name='script-upload'),
    path('scripts/<int:id>/edit/', ScriptUpdateView.as_view(), name='script-update'),
    path('scripts/<int:id>/delete/', ScriptDeleteView.as_view(), name='script-delete'),
    path('scripts/<int:id>/suggestions/', ScriptSuggestionView.as_view(), name='script-suggestions'),
    path('scripts/<int:id>/suggestions/<int:suggestion_id>/<str:action>/', ScriptSuggestionActionView.as_view(), name='script-suggestion-action'),
    path('scripts/<int:id>/scenes/', GenerateScenesView.as_view(), name='generate-scenes'),

    # Scene endpoints
    path('scenes/<int:id>/create/', CreateSceneView.as_view(), name='create-scenes'),
    path('scenes/<int:scene_id>/edit/', EditSceneView.as_view(), name='edit-scene'),
    path('scenes/<int:scene_id>/delete/', DeleteSceneView.as_view(), name='delete-scene'),
    path('scenes/<int:scene_id>/regenerate/', RegenerateSceneView.as_view(), name='regenerate-scene'),
    
    # Shot endpoints
    path('scenes/<int:scene_id>/shots/', GenerateShotsView.as_view(), name='generate-shots'),
    path('shots/<int:shot_id>/done/', MarkShotDoneView.as_view(), name='mark-shot-done'),
    
    # Timeline endpoint
    path('scenes/<int:scene_id>/timeline/', UpdateTimelineView.as_view(), name='update-timeline'),
    
    # Sequence endpoints
    path('sequences/', CreateSequenceView.as_view(), name='create-sequence'),
    
    # Storyboard endpoints
    path('storyboards/', GenerateStoryboardView.as_view(), name='generate-storyboards'),
    path('storyboards/<int:id>/edit/', EditStoryboardView.as_view(), name='edit-storyboard'),
]
