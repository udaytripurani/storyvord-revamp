from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from client.models import ClientCompanyProfile
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from storyvord.exception_handlers import custom_exception_handler

class CrewProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewProfileSerializer

    def get(self, request, format=None):
        try:
            profile = get_object_or_404(CrewProfile, user=request.user)
            serializer = CrewProfileSerializer(profile)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
     
    def put(self, request, format=None):
        try:
            profile = get_object_or_404(CrewProfile, user=request.user)
            serializer = CrewProfileSerializer(profile, data=request.data, partial=True)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class CrewCreditsListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewCreditsSerializer

    def get(self, request, format=None):
        try:
            credits = CrewCredits.objects.filter(crew__user=request.user)
            serializer = CrewCreditsSerializer(credits, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, format=None):
        try:
            serializer = CrewCreditsSerializer(data=request.data)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class CrewCreditsDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewCreditsSerializer

    def get_object(self, pk, user):
        return get_object_or_404(CrewCredits, pk=pk, crew__user=user)

    def get(self, request, pk, format=None):
        try:
            credit = self.get_object(pk, request.user)
            serializer = CrewCreditsSerializer(credit)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk, format=None):
        try:
            credit = self.get_object(pk, request.user)
            serializer = CrewCreditsSerializer(credit, data=request.data, partial=True)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk, format=None):
        try:
            credit = self.get_object(pk, request.user)
            credit.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
class CrewEducationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewEducationSerializer

    def get(self, request, format=None):
        try:
            educations = CrewEducation.objects.filter(crew__user=request.user)
            serializer = CrewEducationSerializer(educations, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, format=None):
        try:
            serializer = CrewEducationSerializer(data=request.data)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class CrewEducationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewEducationSerializer

    def get_object(self, pk, user):
        return get_object_or_404(CrewEducation, pk=pk, crew__user=user)

    def get(self, request, pk, format=None):
        try:
            education = self.get_object(pk, request.user)
            serializer = CrewEducationSerializer(education)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk, format=None):
        try: 
            education = self.get_object(pk, request.user)
            serializer = CrewEducationSerializer(education, data=request.data, partial=True)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk, format=None):
        try:
            education = self.get_object(pk, request.user)
            education.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
# EndorsementfromPeers Views
class EndorsementfromPeersListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EndorsementfromPeersSerializer

    def get(self, request, format=None):
        try:
            endorsements = EndorsementfromPeers.objects.filter(crew__user=request.user)
            serializer = EndorsementfromPeersSerializer(endorsements, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, format=None):
        try:
            serializer = EndorsementfromPeersSerializer(data=request.data)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EndorsementfromPeersDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EndorsementfromPeersSerializer

    def get_object(self, pk, user):
        return get_object_or_404(EndorsementfromPeers, pk=pk, crew__user=user)

    def get(self, request, pk, format=None):
        try: 
            endorsement = self.get_object(pk, request.user)
            serializer = EndorsementfromPeersSerializer(endorsement)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk, format=None):
        try:
            endorsement = self.get_object(pk, request.user)
            serializer = EndorsementfromPeersSerializer(endorsement, data=request.data, partial=True)
            
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk, format=None):
        try:
            endorsement = self.get_object(pk, request.user)
            endorsement.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

# SocialLinks Views
class SocialLinksListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialLinksSerializer

    def get(self, request, format=None):
        try:
            links = SocialLinks.objects.filter(crew__user=request.user)
            serializer = SocialLinksSerializer(links, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, format=None):
        try:
            serializer = SocialLinksSerializer(data=request.data)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class SocialLinksDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialLinksSerializer

    def get_object(self, pk, user):
        return get_object_or_404(SocialLinks, pk=pk, crew__user=user)

    def get(self, request, pk, format=None):
        try:
            link = self.get_object(pk, request.user)
            serializer = SocialLinksSerializer(link)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk, format=None):
        try: 
            link = self.get_object(pk, request.user)
            serializer = SocialLinksSerializer(link, data=request.data, partial=True)

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk, format=None):
        try:
            link = self.get_object(pk, request.user)
            link.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

        

class CrewListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, pk=None):
        try:
            if pk:
                crew_profiles = CrewProfile.objects.filter(pk=pk)
            else:
                crew_profiles = CrewProfile.objects.all()
            response_data = []

            for crew_profile in crew_profiles:
                crew_credits = CrewCredits.objects.filter(crew=crew_profile)
                crew_education = CrewEducation.objects.filter(crew=crew_profile)
                endorsement_from_peers = EndorsementfromPeers.objects.filter(crew=crew_profile)
                social_links = SocialLinks.objects.filter(crew=crew_profile)


                # Serialize the data
                crew_profile_data = CrewProfileSerializer(crew_profile).data
                crew_credits_data = CrewCreditsSerializer(crew_credits, many=True).data
                crew_education_data = CrewEducationSerializer(crew_education, many=True).data
                endorsement_from_peers_data = EndorsementfromPeersSerializer(endorsement_from_peers, many=True).data
                social_links_data = SocialLinksSerializer(social_links, many=True).data

                # Construct the response data for this crew profile
                profile_response_data = {
                    'crew_profile': crew_profile_data,
                    'crew_credits': crew_credits_data,
                    'crew_education': crew_education_data,
                    'endorsement_from_peers_data': endorsement_from_peers_data,
                    'social_links': social_links_data,
                }

                response_data.append(profile_response_data)

            data = {
                'message': 'Success',
                'data': response_data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    

class CrewOnboarding(APIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializers_class = CrewPortfolioSerializer

    def post(self, request):
        try:
            crew_profile = CrewProfile.objects.get(user=request.user)

            user = request.user

            if str(user.user_type) != 'crew':
                raise PermissionError('Only crew can onboard')
        
            if user.steps:
                raise PermissionError('User has already onboarded')
            
            serializer = CrewPortfolioSerializer(data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            serializer.save(crew=crew_profile)

            user.steps = True
            user.user_stage = 2
            user.save()
            
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

# Crew Porfolio and its verification APIS

class CrewPortfolioListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewPortfolioCreateSerializer

    def get(self, request):
        try:
            crew_profile = CrewProfile.objects.get(user=request.user)

            # List CrewPortfolios associated with the CrewProfile
            portfolios = CrewPortfolio.objects.filter(crew=crew_profile)
            serializer = CrewPortfolioSerializer(portfolios, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request):
        try:
            crew_profile = CrewProfile.objects.get(user=request.user)

            serializer = CrewPortfolioCreateSerializer(data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            portfolio = serializer.save(crew=crew_profile)
            data = {
                'message': 'Success',
                'data': CrewPortfolioSerializer(portfolio).data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response


class CrewPortfolioDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CrewPortfolioSerializer

    def get_object(self, pk):
        try:
            return CrewPortfolio.objects.get(pk=pk)
        except CrewPortfolio.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            portfolio = self.get_object(pk)
            # if portfolio is None:
                # return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
            # Check if the portfolio belongs to the authenticated user's CrewProfile
            if portfolio.crew.user != request.user:
                return Response({'status': False,
                                'code': status.HTTP_403_FORBIDDEN,
                                "message": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        
            serializer = CrewPortfolioSerializer(portfolio)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk):
        try:
            portfolio = self.get_object(pk)
            # if portfolio is None:
                # return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
            # Check if the portfolio belongs to the authenticated user's CrewProfile
            if portfolio.crew.user != request.user:
                return Response({'status': False,
                                'code': status.HTTP_403_FORBIDDEN,
                                 "message": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

            serializer = CrewPortfolioSerializer(portfolio, data=request.data, partial=True)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk):
        try:
            portfolio = self.get_object(pk)
            # if portfolio is None:
                # return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
            # Check if the portfolio belongs to the authenticated user's CrewProfile
            if portfolio.crew.user != request.user:
                return Response({'status': False,
                                'code': status.HTTP_403_FORBIDDEN,
                                 "detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        
            portfolio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response


class VerifyClientReference(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientReferenceVerificationSerializer

    def post(self, request, pk):
        try:
            portfolio = CrewPortfolio.objects.filter(id=pk).first()
            # if not portfolio:
                # return Response({"detail": "Crew Portfolio not found."}, status=status.HTTP_404_NOT_FOUND)
        
            if portfolio.crew.user != request.user:
                return Response({'status': False,
                                 'code': status.HTTP_403_FORBIDDEN,  
                                 "message": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

            serializer = ClientReferenceVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            verification, created = ClientReferenceVerification.objects.get_or_create(crew_portfolio=portfolio, defaults=serializer.validated_data)
            if not created:
                for attr, value in serializer.validated_data.items():
                    setattr(verification, attr, value)
                verification.save()
            portfolio.verification_type = 'client_reference'
            portfolio.client_reference_verification = verification
            portfolio.verified = True
            portfolio.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class VerifyImbdLink(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImbdLinkVerificationSerializer

    def post(self, request, pk):
        try:
            portfolio = CrewPortfolio.objects.filter(id=pk).first()
            # if not portfolio:
                # return Response({"detail": "Crew Portfolio not found."}, status=status.HTTP_404_NOT_FOUND)
        
            if portfolio.crew.user != request.user:
                return Response({'status': False,
                                 'code': status.HTTP_403_FORBIDDEN,
                                 "message": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

            serializer = ImbdLinkVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            verification, created = ImbdLinkVerification.objects.get_or_create(crew_portfolio=portfolio, defaults=serializer.validated_data)
            if not created:
                for attr, value in serializer.validated_data.items():
                    setattr(verification, attr, value)
                verification.save()
            portfolio.verification_type = 'imbd_link'
            portfolio.imbd_link_verification = verification
            portfolio.verified = True
            portfolio.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class VerifyWorkSample(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkSampleVerificationSerializer

    def post(self, request, pk):
        try:
            portfolio = CrewPortfolio.objects.filter(id=pk).first()
            # if not portfolio:
                # return Response({"detail": "Crew Portfolio not found."}, status=status.HTTP_404_NOT_FOUND)
        
            if portfolio.crew.user != request.user:
                return Response({'status': False,
                                 'code': status.HTTP_403_FORBIDDEN,
                                 "detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

            serializer = WorkSampleVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            verification, created = WorkSampleVerification.objects.get_or_create(crew_portfolio=portfolio, defaults=serializer.validated_data)
            if not created:
                for attr, value in serializer.validated_data.items():
                    setattr(verification, attr, value)
                verification.save()
            portfolio.verification_type = 'work_sample'
            portfolio.work_sample_verification = verification
            portfolio.verified = True
            portfolio.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class VerifyEmailAgreement(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailAgreementSerializer

    def post(self, request, pk):
        try:
            portfolio = CrewPortfolio.objects.filter(id=pk).first()
            if not portfolio:
                return Response({"detail": "Crew Portfolio not found."}, status=status.HTTP_404_NOT_FOUND)
        
            if portfolio.crew.user != request.user:
                return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

            serializer = EmailAgreementSerializer(data=request.data)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            verification, created = EmailAgreement.objects.get_or_create(crew_portfolio=portfolio, defaults=serializer.validated_data)
            if not created:
                for attr, value in serializer.validated_data.items():
                    setattr(verification, attr, value)
                verification.save()
            portfolio.verification_type = 'email_agreement'
            portfolio.email_agreement_verification = verification
            portfolio.verified = True
            portfolio.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
# All Projects

class UserProjectsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get(self, request):
        try:
            user = request.user
            projects = Project.objects.filter(crew_profiles=user)
        
            serializer = ProjectSerializer(projects, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
class CompanyProjectsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get(self, request):
        try:
            user = request.user
            projects = Project.objects.filter(selected_crew=user)
        
            company_projects = defaultdict(list)
        
            for project in projects:
                creator = project.user  
            
                company_profile = ClientCompanyProfile.objects.get(user=creator)
                company_name = company_profile.company_name
            
                project_data = ProjectSerializer(project).data
                company_projects[company_name].append(project_data)
        
            response_data = [
                {
                    "company_name": company,
                    "projects": projects
                }
                for company, projects in company_projects.items()
            ]

            data = {
                'message': 'Success',
                'data': response_data
            }
        
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import CrewProfile
from accounts.models import PersonalInfo
from .serializers import CrewProfileSerializer
from project.models import ProjectInvite
class CrewProfileSearchView(APIView):
    """
    API view to search crew profiles with invitation status from logged-in user
    """
    permission_classes =[permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            # Extract search parameters
            location_query = request.data.get('location', '')
            skills_query = request.data.get('skills', '')
            name_query = request.data.get('name', '')

            # Get base crew profiles
            crew_profiles = CrewProfile.objects.filter(
                Q(personal_info__full_name__icontains=name_query) &
                Q(personal_info__location__icontains=location_query) &
                Q(skills__icontains=skills_query),
                active=True
            ).select_related('personal_info__user')

            # Get all crew user IDs
            crew_user_ids = [cp.personal_info.user.id for cp in crew_profiles]

            # Get all invites sent by current user to these crew members
            invites = ProjectInvite.objects.filter(
                inviter=request.user,
                invitee_id__in=crew_user_ids
            )

            # Create invitation map {crew_user_id: {project_id: invite_data}}
            invitation_map = defaultdict(dict)
            for invite in invites:
                invitation_map[invite.invitee_id][invite.project_id] = {
                    "status": invite.status,
                    "updated_at": invite.updated_at
                    
                }

            # Serialize results
            serializer = CrewProfileSerializer(crew_profiles, many=True)
            response_data = []
            
            # Add invitation status to each crew profile
            for profile, data in zip(crew_profiles, serializer.data):
                user_id = profile.personal_info.user.id
                invitations = []
                
                # Get all projects for this crew member
                for project_id, invite_data in invitation_map.get(user_id, {}).items():
                    invitations.append({
                        "project_id": project_id,
                        "status": invite_data['status'],
                        "last_updated": invite_data['updated_at']
                        
                    })
                
                data['invitations'] = sorted(invitations, key=lambda x: x['last_updated'], reverse=True)
                response_data.append(data)

            return Response({
                'message': 'Success',
                'data': response_data
            }, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {'message': 'An error occurred', 'details': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
