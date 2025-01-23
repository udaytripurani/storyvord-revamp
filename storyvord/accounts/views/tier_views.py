from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from ..models import User, UserType, Tier
import logging

logger = logging.getLogger(__name__)

class SelectTierView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            tier_id = request.data.get('tier_id')
            logger.info(f"User {user.email} requesting tier change to {tier_id}")

            if not tier_id:
                logger.warning("Tier ID not provided in request.")
                return Response({
                    "status": False,
                    "code": 400,
                    "message": "Tier ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                tier = Tier.objects.get(id=tier_id)
                logger.info(f"Tier {tier.name} found for ID {tier_id}")
            except Tier.DoesNotExist:
                logger.warning(f"Tier ID {tier_id} does not exist.")
                return Response({
                    "status": False,
                    "code": 404,
                    "message": "Tier not found."
                }, status=status.HTTP_404_NOT_FOUND)

            if tier.user_type != user.user_type:
                logger.warning(f"Invalid tier selection for user {user.email}: Tier ID {tier_id} not compatible with user type.")
                return Response({
                    "status": False,
                    "code": 400,
                    "message": "Invalid tier for user type."
                }, status=status.HTTP_400_BAD_REQUEST)

            if user.tier == tier:
                logger.info(f"User {user.email} is already on the requested tier {tier.name}.")
                return Response({
                    "status": False,
                    "code": 400,
                    "message": "User is already on this tier."
                }, status=status.HTTP_400_BAD_REQUEST)

            if tier.is_default:
                user.user_stage = '3'
                user.save()
                user.assign_default_tier()
                logger.info(f"User {user.email} assigned to default tier {tier.name}.")
                return Response({
                    "status": True,
                    "code": 200,
                    "message": "Default tier selected successfully.",
                    "data": {
                        "tier": tier.name,
                        "pricing": tier.price
                    }
                }, status=status.HTTP_200_OK)

            # Demo payment gateway logic
            # For now, just check if the payment is successful
            if tier.price > 0:
                payment_successful = True
                if not payment_successful:
                    logger.error(f"Payment failed for user {user.email} for tier {tier.name}.")
                    return Response({
                        "status": False,
                        "code": 402,
                        "message": "Payment failed. Please try again later."
                    }, status=status.HTTP_402_PAYMENT_REQUIRED)

            user.tier = tier
            user.save()
            logger.info(f"User {user.email} tier updated to {tier.name}.")

            return Response({
                "status": True,
                "code": 200,
                "message": "Tier selected successfully.",
                "data": {
                    "tier": tier.name,
                    "pricing": tier.price
                }
            }, status=status.HTTP_200_OK)
        except AuthenticationFailed:
            logger.error("Authentication credentials were not provided or are invalid.")
            return Response({
                "status": False,
                "code": 401,
                "message": "Authentication credentials were not provided or are invalid."
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({
                "status": False,
                "code": 500,
                "message": "An unexpected error occurred. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
