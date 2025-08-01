from rest_framework.views import APIView
from  rest_framework import generics
from .serializers import RoomSerializer
from .models import Room
from rest_framework.permissions import IsAuthenticated

class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]


