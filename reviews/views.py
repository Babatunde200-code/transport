from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer
from travels.models import Travel
from accounts.models import CustomUser

class ReviewListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        travel_id = request.query_params.get('travel')
        if not travel_id:
            return Response({"detail": "Missing travel id"}, status=400)
        reviews = Review.objects.filter(travel_id=travel_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, reviewer=request.user)
        except Review.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, reviewer=request.user)
        except Review.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        review.delete()
        return Response({"detail": "Deleted."})

class DriverReviewsView(APIView):
    def get(self, request, user_id):
        travels = Travel.objects.filter(driver__id=user_id)
        reviews = Review.objects.filter(travel__in=travels)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
