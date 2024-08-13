# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from .models import KebabSpot
# from .serializers import KebabSpotSerializer
#
# class KebabSpotViewSet(viewsets.ModelViewSet):
#     queryset = KebabSpot.objects.all()
#     serializer_class = KebabSpotSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)