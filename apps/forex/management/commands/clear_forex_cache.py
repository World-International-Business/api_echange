from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = "Vide le cache Redis des taux de change (prefixe live_rate: et rates:)"

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Vider tout le cache (flushdb)')

    def handle(self, *args, **options):
        if options['all']:
            try:
                from django_redis import get_redis_connection
                con = get_redis_connection('default')
                con.flushdb()
                self.stdout.write(self.style.SUCCESS('✅ Cache Redis entierement vide (flushdb).'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur flushdb : {e}'))
        else:
            prefixes = ['live_rate:*', 'rates:*', ':1:live_rate:*', ':1:rates:*']
            deleted = 0
            try:
                from django_redis import get_redis_connection
                con = get_redis_connection('default')
                for pattern in prefixes:
                    keys = con.keys(pattern)
                    if keys:
                        deleted += con.delete(*keys)
                self.stdout.write(self.style.SUCCESS(f'✅ {deleted} cle(s) supprimee(s) du cache Redis.'))
            except Exception as e:
                cache.clear()
                self.stdout.write(self.style.WARNING(f'⚠  Redis direct inaccessible, cache.clear() utilise : {e}'))
