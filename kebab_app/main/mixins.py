from django.http import JsonResponse

class RatingMixin:
    def __init__(self, rating_model, related_object_field):
        self.rating_model = rating_model
        self.related_object_field = related_object_field

    def update_or_create_rating(self, user, instance, rating_value):
        update_kwargs = {
            'user': user,
            self.related_object_field: instance,
            'defaults': {'value': int(rating_value)}
        }
        self.rating_model.objects.update_or_create(**update_kwargs)
        return {
            'status': 'success',
            'avg_rating': instance.average_rating()
        }

    def handle_rating_update(self, request, instance):
        rating_value = request.POST.get('rating')
        if rating_value:
            return JsonResponse(
                self.update_or_create_rating(
                    request.user,
                    instance,
                    rating_value
                )
            )
        return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)