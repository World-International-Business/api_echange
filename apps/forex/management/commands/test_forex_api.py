import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache


class Command(BaseCommand):
    help = "Teste la recuperation de taux en temps reel depuis les providers externes"

    PROVIDERS = [
        {
            'name': 'ExchangeRate-API (gratuit, sans cle)',
            'url': 'https://api.exchangerate-api.com/v4/latest/EUR',
            'headers': None,
            'params': None,
            'extract': lambda data: data['rates']['USD'],
            'pair': 'EUR/USD',
        },
        {
            'name': 'ECB (Banque Centrale Europeenne)',
            'url': 'https://www.frankfurter.app/latest?from=EUR&to=USD',
            'headers': None,
            'params': None,
            'extract': lambda data: data['rates']['USD'],
            'pair': 'EUR/USD',
        },
        {
            'name': 'Fixer.io',
            'url': 'https://api.apilayer.com/fixer/latest',
            'headers': {'apikey': getattr(settings, 'FIXER_API_KEY', '')},
            'params': {'base': 'EUR', 'symbols': 'USD'},
            'extract': lambda data: data['rates']['USD'],
            'pair': 'EUR/USD',
        },
        {
            'name': 'OpenExchangeRates',
            'url': 'https://openexchangerates.org/api/latest.json',
            'headers': None,
            'params': {'app_id': getattr(settings, 'OPENEXCHANGERATES_APP_ID', ''), 'symbols': 'EUR,USD'},
            'extract': lambda data: data['rates']['EUR'],
            'pair': 'USD/EUR',
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument('--pair', type=str, default='EUR/USD', help='Paire de devises (ex: EUR/USD)')
        parser.add_argument('--provider', type=str, default=None, help='Nom du provider a tester')
        parser.add_argument('--cache', action='store_true', help='Tester aussi le cache Redis')

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('\n===== TEST FOREX API PROVIDERS =====\n'))

        if options['cache']:
            self._test_cache()

        success = False
        for provider in self.PROVIDERS:
            if options['provider'] and options['provider'].lower() not in provider['name'].lower():
                continue

            if not self._should_test(provider):
                self.stdout.write(self.style.WARNING(f"⏭  {provider['name']} — cle API manquante, ignore."))
                continue

            self.stdout.write(f"\n🔍 Test de {provider['name']} ({provider['pair']})...")
            rate = self._fetch(provider)
            if rate is not None:
                self.stdout.write(self.style.SUCCESS(
                    f"   ✅ Taux {provider['pair']} : {rate}\n"
                    f"   URL : {provider['url']}"
                ))
                self._save_to_cache(provider['pair'], rate)
                success = True
                if not options['provider']:
                    break

        if not success:
            self.stdout.write(self.style.ERROR(
                '\n⚠  Aucun provider accessible. Verifiez :\n'
                '   - Les cles API dans le .env (FIXER_API_KEY, OPENEXCHANGERATES_APP_ID)\n'
                '   - La connexion internet\n'
                '   - La disponibilite des services\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('\n===== TEST TERMINE AVEC SUCCES =====\n'))

    def _should_test(self, provider):
        if 'apikey' in (provider.get('headers') or {}):
            return bool(provider['headers']['apikey'])
        if provider.get('params') and 'app_id' in provider['params']:
            return bool(provider['params']['app_id'])
        return True

    def _fetch(self, provider):
        try:
            resp = requests.get(
                provider['url'],
                headers=provider['headers'],
                params=provider['params'],
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
            rate = Decimal(str(provider['extract'](data)))
            return rate
        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR(f"   ❌ Timeout (>8s)"))
        except requests.exceptions.HTTPError as e:
            self.stdout.write(self.style.ERROR(f"   ❌ HTTP {e.response.status_code} : {e}"))
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR(f"   ❌ Connexion impossible"))
        except (KeyError, TypeError) as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Structure JSON inattendue : {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erreur : {e}"))
        return None

    def _save_to_cache(self, pair, rate):
        try:
            key = f"live_rate:{pair.replace('/', ':')}"
            cache.set(key, str(rate), timeout=300)
            self.stdout.write(f"   💾 Taux mis en cache Redis (cle: {key}, TTL: 5min)")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠  Cache Redis indisponible : {e}"))

    def _test_cache(self):
        self.stdout.write('\n🔌 Test du cache Redis...')
        try:
            cache.set('forex_test_ping', 'pong', 10)
            val = cache.get('forex_test_ping')
            if val == 'pong':
                self.stdout.write(self.style.SUCCESS('   ✅ Redis operationnel'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠  Redis repond mais valeur incorrecte'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Redis inaccessible : {e}'))
