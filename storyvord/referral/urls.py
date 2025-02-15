from django.urls import path
from .views import *

urlpatterns = [
    path('projects/add-crew/', AddCrewToProjectView.as_view(), name='add-crew-to-project'),
    path('invitations/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('invitations/reject/', RejectInvitationView.as_view(), name='reject-invitation'),
    path('register-with-referral/', RegisterWithReferralCrewView.as_view(), name='register-with-referral'),
    path('invitations/', CrewInvitationsView.as_view(), name='crew-invitations'),
    path('client/crew-invitations/<str:project_id>/', ClientCrewInvitationsView.as_view(), name='client-crew-invitations'),
    path('crew/invitation-details/', ReferralCodeCrewDetailView.as_view(), name='invitation-details'),
    
    path('company/invite/', AddEmployeeToClientProfileView.as_view(), name='client-invite'),
    path('company/invitations/accept/', AcceptClientInvitationView.as_view(), name='client-invite-accept'),
    path('company/invitations/reject/', RejectClientInvitationView.as_view(), name='client-invite-reject'),
    path('company/register-with-referral/', RegisterWithReferralView.as_view(), name='client-register-with-referral'),
    path('company/invitations/', EmployeeInvitationsView.as_view(), name='client-invitations'),
    path('company/employee/invitations/', EmployeeInvitationsClientView.as_view(), name='client-invitations'),
    path('company/client/employee-invitations/', ClientEmployeeInvitationsView.as_view(), name='client-employee-invitations'),
    path('company/invitation-details/', ReferralCodeDetailView.as_view(), name='invitation-details'),
]
