from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from .models import APIClient


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_ok = True
        cache_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        try:
            cache.set('health_check', '1', 5)
            cache_ok = cache.get('health_check') == '1'
        except Exception:
            cache_ok = False

        return Response({
            'status': 'ok' if db_ok and cache_ok else 'degraded',
            'service': 'ForexPlatform API',
            'version': '1.0.0',
            'timestamp': now().isoformat(),
            'checks': {
                'database': 'ok' if db_ok else 'error',
                'cache': 'ok' if cache_ok else 'error',
            }
        })


class APIKeyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keys = APIClient.objects.filter(user=request.user).values(
            'id', 'name', 'api_key_prefix', 'tier',
            'quota_requests_per_hour', 'total_requests',
            'expires_at', 'is_active', 'created_at'
        )
        return Response({'success': True, 'api_keys': list(keys)})


class APIKeyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name', '').strip()
        tier = request.data.get('tier', 'free')
        if not name:
            return Response({'success': False, 'error': 'Name is required.'}, status=400)
        if tier not in dict(APIClient.TIER_CHOICES):
            return Response({'success': False, 'error': 'Invalid tier.'}, status=400)

        raw_key, key_hash, prefix = APIClient.generate_key()
        quota = APIClient.QUOTA_MAP.get(tier, 100)
        APIClient.objects.create(
            user=request.user,
            name=name,
            api_key_prefix=prefix,
            api_key_hash=key_hash,
            tier=tier,
            quota_requests_per_hour=quota,
        )
        return Response({'success': True, 'raw_key': raw_key}, status=201)


class APIKeyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            key = APIClient.objects.get(pk=pk, user=request.user)
            key.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except APIClient.DoesNotExist:
            return Response({'success': False, 'error': 'API key not found.'}, status=404)
