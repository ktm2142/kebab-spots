# from rest_framework import serializers
# from .models import KebabSpot, KebabSpotPhoto
#
# class KebabSpotSerializer(serializers.ModelSerializer):
#     photos = serializers.ListField(
#         child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
#         write_only=True, required=False
#     )
#
#     class Meta:
#         model = KebabSpot
#         fields = ['name', 'description', 'location', 'notes', 'payed_or_free', 'private_property', 'parking', 'toilets', 'gazebos', 'tables', 'camping_places', 'swimming_spot', 'place_for_fire', 'trash_bins', 'photos']
#
#     def create(self, validated_data):
#         photos = validated_data.pop('photos', [])
#         kebab_spot = KebabSpot.objects.create(**validated_data)
#         for photo in photos:
#             KebabSpotPhoto.objects.create(kebab_spot=kebab_spot, image=photo)
#         return kebab_spot