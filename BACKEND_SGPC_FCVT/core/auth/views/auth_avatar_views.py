"""
View para actualización del avatar del usuario autenticado.
"""

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth.serializers.auth_avatar_serializers import AvatarUpdateSerializer


class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        return self._update_avatar(request)

    def post(self, request):
        return self._update_avatar(request)

    def _update_avatar(self, request):
        user = request.user

        if "avatar" not in request.data and "avatar" not in request.FILES:
            return Response(
                {"avatar": "Debe adjuntar una imagen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AvatarUpdateSerializer(
            user,
            data=request.data,
            partial=False,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db(fields=["avatar"])

        avatar_url = None
        if getattr(user, "avatar", None) and getattr(user.avatar, "url", None):
            try:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            except Exception:
                avatar_url = user.avatar.url

        return Response(
            {"avatar_url": avatar_url},
            status=status.HTTP_200_OK,
        )