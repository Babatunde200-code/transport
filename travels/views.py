from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Travel
from .serializers import TravelSerializer

class TravelListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        travels = Travel.objects.filter(driver=request.user)
        serializer = TravelSerializer(travels, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TravelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(driver=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TravelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Travel.objects.get(pk=pk, driver=user)
        except Travel.DoesNotExist:
            return None

    def put(self, request, pk):
        travel = self.get_object(pk, request.user)
        if not travel:
            return Response({"detail": "Not found."}, status=404)
        serializer = TravelSerializer(travel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        travel = self.get_object(pk, request.user)
        if not travel:
            return Response({"detail": "Not found."}, status=404)
        travel.delete()
        return Response(status=204)
