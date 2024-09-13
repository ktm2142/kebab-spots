from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.paginator import Paginator
from django.db.models import Prefetch, Count, Q, Avg
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable, GeocoderQueryError, GeocoderQuotaExceeded
from django.core.cache import cache
from .forms import CommentForm, KebabSpotFilterForm
from .models import Comment, CommentRating, Rating, KebabSpot
import logging

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="KebabSpots/1.0 (rghnmju@gmail.com)")

    def get_coordinates(self, address):
        cache_key = f"geocode_{address}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            location = self.geolocator.geocode(address)
            if location:
                result = (location.latitude, location.longitude)
                cache.set(cache_key, result, 86400)
                return result
        except GeocoderTimedOut:
            logger.warning(f"Timeout error while geocoding address: {address}")
        except GeocoderServiceError:
            logger.error(f"Geocoding service error for address: {address}")
        except GeocoderUnavailable:
            logger.error("Geocoding service is unavailable")
        except GeocoderQueryError:
            logger.error(f"Invalid geocoding query for address: {address}")
        except GeocoderQuotaExceeded:
            logger.error("Geocoding quota exceeded")
        except Exception as e:
            logger.exception(f"Unexpected error during geocoding: {str(e)}")
        return None


class NearbyKebabSpotsService:
    def get(self, request, *args, **kwargs):
        filter_params, radius = FilteringService.get_filter_params(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            lat = request.GET.get('lat')
            lng = request.GET.get('lng')
            if lat and lng:
                user_location = Point(float(lng), float(lat), srid=4326)
                kebab_spots = FilteringService.get_kebab_spots(user_location, radius, filter_params)
                spots_data = [{
                    'id': spot.id,
                    'name': spot.name,
                    'lat': spot.location.y,
                    'lng': spot.location.x,
                    'url': reverse('main:kebab_spot_detail', args=[spot.id]),
                    'avg_rating': round(spot.avg_rating, 1) if spot.avg_rating else 0
                } for spot in kebab_spots]
                return JsonResponse(spots_data, safe=False)
            else:
                return JsonResponse({'error': 'Геолокація не надана'}, status=400)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kebab_spots_json'] = []
        context['filter_form'] = KebabSpotFilterForm(self.request.GET or None)
        return context


class SearchKebabSpotsService:
    def get(self, request, *args, **kwargs):
        if not request.GET.get('q'):
            return redirect('main:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query

        filter_params, radius = FilteringService.get_filter_params(self.request)

        if query:
            geocoding_service = GeocodingService()
            coordinates = geocoding_service.get_coordinates(query)

            if coordinates:
                user_location = Point(coordinates[1], coordinates[0], srid=4326)
                kebab_spots = FilteringService.get_kebab_spots(user_location, radius, filter_params)

                context['search_coordinates'] = {
                    'lat': coordinates[0],
                    'lng': coordinates[1]
                }
                context['kebab_spots_json'] = [{
                    'id': spot.id,
                    'name': spot.name,
                    'lat': spot.location.y,
                    'lng': spot.location.x,
                    'url': reverse('main:kebab_spot_detail', args=[spot.id]),
                    'avg_rating': round(spot.avg_rating, 1) if spot.avg_rating else 0
                } for spot in kebab_spots]
            else:
                context['error_message'] = "Не вдалося знайти вказане місце. Перевірте правильність написання."

        context['filter_form'] = KebabSpotFilterForm(self.request.GET or None)
        return context


class FilteringService:
    @staticmethod
    def get_filter_params(request):
        filter_params = request.GET.dict()
        radius = int(filter_params.pop('radius', 10))
        return filter_params, radius

    @staticmethod
    def get_kebab_spots(user_location, radius=10, filter_params=None):
        queryset = KebabSpot.objects.annotate(
            distance=Distance('location', user_location),
            avg_rating=Avg('ratings__value')
        ).filter(distance__lte=D(km=radius))

        if filter_params:
            for key, value in filter_params.items():
                if value == 'on':
                    queryset = queryset.filter(**{key: True})

        return queryset


class CommentService:
    @staticmethod
    def get_paginated_comments(kebab_spot, page_number):
        comments = (Comment.objects
                    .filter(kebab_spot=kebab_spot)
                    .select_related('user')
                    .prefetch_related('comment_photos', Prefetch(
                        'ratings',
                        queryset=CommentRating.objects.select_related('user'),
                        to_attr='comment_rating')
                    )
                    .annotate(
                        upvotes=Count('ratings', filter=Q(ratings__is_positive=True)),
                        downvotes=Count('ratings', filter=Q(ratings__is_positive=False))
                    )
                    .order_by('-created_at'))
        paginator = Paginator(comments, 10)
        return paginator.get_page(page_number)

    @staticmethod
    def create_comment(user, kebab_spot, form_data, files):
        comment_form = CommentForm(form_data, files)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = user
            comment.kebab_spot = kebab_spot
            comment_form.save()
            return True, comment
        return False, comment_form

    @staticmethod
    def vote_comment(user, comment, vote_type):
        is_positive = (vote_type == 'up')
        CommentRating.objects.update_or_create(
            comment=comment,
            user=user,
            defaults={'is_positive': is_positive}
        )
        upvotes = CommentRating.objects.filter(comment=comment, is_positive=True).count()
        downvotes = CommentRating.objects.filter(comment=comment, is_positive=False).count()
        return {'upvotes': upvotes, 'downvotes': downvotes}

    @staticmethod
    def handle_comment_vote(request, kebab_spot):
        comment_id = request.POST.get('comment_id')
        vote_type = request.POST.get('vote_type')
        if comment_id and vote_type:
            try:
                comment = Comment.objects.get(pk=comment_id, kebab_spot=kebab_spot)
                result = CommentService.vote_comment(request.user, comment, vote_type)
                return JsonResponse({
                    'status': 'success',
                    'upvotes': result['upvotes'],
                    'downvotes': result['downvotes']
                })
            except Comment.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Comment not found'}, status=404)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


class KebabSpotRatingService:
    @staticmethod
    def update_or_create_rating(user, kebab_spot, rating_value):
        rating, created = Rating.objects.update_or_create(
            user=user,
            kebab_spot=kebab_spot,
            defaults={'value': int(rating_value)}
        )
        return {
            'status': 'success',
            'avg_rating': kebab_spot.average_rating()
        }

    @staticmethod
    def handle_post_request(view_instance, request, spot):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Обробляємо ajax-запит і делегуємо відповідній логіці
            if 'rating' in request.POST:
                return KebabSpotRatingService.handle_rating_update(request, spot)
            else:
                return CommentService.handle_comment_vote(request, spot)
        # Якщо це не ajax-запит, то це коментар
        return view_instance.handle_comment_form(request, spot)

    @staticmethod
    def handle_rating_update(request, kebab_spot):
        rating_value = request.POST.get('rating')
        if rating_value:
            return JsonResponse(
                KebabSpotRatingService.update_or_create_rating(
                    request.user,
                    kebab_spot,
                    rating_value
                )
            )
        return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)

