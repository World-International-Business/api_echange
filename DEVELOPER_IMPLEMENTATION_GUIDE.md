# 👨‍💻 GUIDE D'IMPLÉMENTATION POUR LES DÉVELOPPEURS

**Objectif:** Expliquer comment implémenter chaque tâche **étape par étape** avec des exemples concrets et testables.

---

# 🎯 TABLE DES MATIÈRES
1. [SPRINT 1 - Cadrage & Architecture](#sprint-1)
2. [SPRINT 2 - Modèles de Données & Sync](#sprint-2)
3. [SPRINT 3 - Endpoints & Sécurité](#sprint-3)
4. [SPRINT 4 - Tests & Documentation](#sprint-4)
5. [SPRINT 5 - Déploiement](#sprint-5)
6. [SPRINT 6 - Stabilisation](#sprint-6)

---

# SPRINT 1: CADRAGE & ARCHITECTURE

## 🎯 Tâche 1: Périmètre MVP Validé

### 💡 C'est Quoi?
Valider que **tout le monde est d'accord** sur ce qui doit être fait. Pas de "je croyais que...!" à la fin.

### 📝 À Faire
1. **Réunion de cadrage** (1-2 jours)
   - Rencontre avec le PO (Product Owner)
   - Poser les questions clés:
     - Quel est le **but principal** de l'API?
     - **Quels endpoints** absolument nécessaires?
     - Combien de **devises** à supporter?
     - **Fréquence** de mise à jour des taux?

2. **Rédiger le document SPECIFICATION.md** (2-3 jours)
   ```markdown
   # Spécifications - API Taux de Change
   
   ## 1. Objectif
   Permettre aux utilisateurs de consulter et convertir des devises.
   
   ## 2. Scope MVP
   ### Endpoints
   - GET /currencies → Liste des devises
   - GET /rates → Taux actuels
   - POST /convert → Convertir un montant
   - GET /health → Status de l'API
   
   ### Devises supportées
   EUR, USD, GBP, JPY, CAD, AUD, CHF, CNY, INR, MXN
   
   ## 3. Constraints
   - Temps de réponse < 200ms
   - Authenticatio obligatoire
   - Rate limit: 100 req/min
   
   ## 4. Non-Scope (Phase 2)
   - Historique graphique
   - Alerts de change
   - Webhooks
   ```

3. **Faire approuver** (1-2 jours)
   - Présenter au PO et à la direction
   - Recueillir feedback
   - Signer l'approbation (email de confirmation)

### ✅ Vous Saurez C'est Fini Quand
- ✓ Fichier SPECIFICATION.md existe
- ✓ PO a signé l'approbation (email)
- ✓ Pas d'ambiguïté sur ce qui doit être fait
- ✓ Tout le monde a la même compréhension

### 🚨 Pièges Courants
- ❌ Oublier de signer → Faire un mail de confirmation
- ❌ Scope trop large → Refuser les features en dehors du MVP
- ❌ Ambiguïtés → Poser des questions jusqu'à clarté complète

---

## 🎯 Tâche 2: Provider de Taux Sélectionné

### 💡 C'est Quoi?
Choisir **qui va nous fournir les taux de change** (Fixer.io, Open Exchange Rates, etc.)

### 📝 À Faire

#### Étape 1: Faire une Liste de Providers (1-2 jours)
```
Fixer.io
- Avantages: Simple, fiable, bon support
- Coût: ~10$/mois plan basic
- Uptime: 99.9%
- Limitations: 100 requêtes/mois en free

Open Exchange Rates
- Avantages: Beaucoup de devises, flexible
- Coût: ~12$/mois
- Uptime: 99.8%
- Limitations: Rate limit 1000/mois en free

Polygon.io
- Avantages: API moderne, bien documentée
- Coût: ~35$/mois
- Uptime: 99.95%
- Limitations: Forex disponible en paid

AlphaVantage
- Avantages: Gratuit (limité)
- Coût: Gratuit
- Uptime: 95%
- Limitations: 5 calls/min seulement
```

#### Étape 2: Tester Chaque Provider (2-3 jours)

```bash
# Pour Fixer.io
curl "https://api.fixer.io/latest?access_key=YOUR_KEY&base=EUR&symbols=USD,GBP"

# Pour Open Exchange Rates
curl "https://openexchangerates.org/api/latest.json?app_id=YOUR_KEY&base=EUR"

# Pour Polygon
curl "https://api.polygon.io/v1/forex/snapshot?apikey=YOUR_KEY"
```

**À évaluer:**
- ✓ La réponse est-elle claire et structurée?
- ✓ Les taux sont-ils à jour?
- ✓ Le support API est-il bon?
- ✓ La documentation est-elle claire?

#### Étape 3: Créer une Matrice de Comparaison (1 jour)

| Critère | Fixer | Open Exchange | Polygon | Winner |
|---------|-------|---------------|---------|--------|
| Coût | $10 | $12 | $35 | Fixer |
| Uptime | 99.9% | 99.8% | 99.95% | Polygon |
| Facilité API | 9/10 | 8/10 | 8/10 | Fixer |
| Devises | 150+ | 200+ | 150+ | Open Exchange |
| Support | Bon | Bon | Très bon | Polygon |
| **Note Finale** | **8/10** | **7/10** | **8/10** | **Fixer** |

#### Étape 4: Communiquer le Choix (1 jour)
```
Email au Tech Lead:

Subject: Provider Taux de Change Sélectionné - Fixer.io

Après évaluation de 3 providers, je recommande Fixer.io:

✓ Avantages:
  - Coût faible ($10/mois)
  - API simple et bien documentée
  - Uptime excellent (99.9%)
  - Support réactif

⚠️ Limitations:
  - 100 requêtes/mois seulement en plan free
  - Pas d'historique en free

📋 Prochaines Étapes:
  1. Souscrire au plan basic ($10/mois)
  2. Générer une clé API
  3. Tester l'intégration en Sprint 2

Clé API testée: ✓
```

### ✅ Vous Saurez C'est Fini Quand
- ✓ 1 provider choisi et justifié
- ✓ Clé API fonctionnelle et testée
- ✓ Documentation du provider stockée dans le projet
- ✓ Tout le monde sait c'est qui le provider

### 🚨 Pièges Courants
- ❌ Choisir un provider gratuit qui s'avère trop limité → Tester en free tier d'abord
- ❌ Oublier de vérifier les limites (rate limit, devises) → Lire les docs en détail
- ❌ Ne pas sauvegarder la clé API → Mettre dans .env.example

---

## 🎯 Tâche 3: Environnement Configuré

### 💡 C'est Quoi?
Avoir un environnement de développement **complet et prêt** pour coder.

### 📝 À Faire - Détaillé

#### Étape 1: Créer le Projet Django (1 jour)

```bash
# 1. Créer le dossier
mkdir -p c:\Users\Utilisateur\Desktop\apiexchange
cd c:\Users\Utilisateur\Desktop\apiexchange

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 4. Créer le requirements.txt avec les libs de base
cat > requirements.txt << 'EOF'
Django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.0.0
celery==5.3.1
redis==5.0.0
python-dotenv==1.0.0
psycopg2-binary==2.9.6
requests==2.31.0
drf-spectacular==0.26.2
gunicorn==21.2.0
pytest==7.4.0
pytest-django==4.5.2
coverage==7.2.0
EOF

# 5. Installer les packages
pip install -r requirements.txt
```

#### Étape 2: Créer la Structure Django

```bash
# Créer le projet Django (dossier parent)
django-admin startproject forex_platform .

# Créer les apps
python manage.py startapp api_gateway
python manage.py startapp core
python manage.py startapp forex
python manage.py startapp transfers
```

**Résultat:**
```
apiexchange/
├── manage.py
├── requirements.txt
├── venv/
├── forex_platform/           # Dossier config
│   ├── settings.py          # À modifier
│   ├── urls.py              # À modifier
│   ├── celery.py            # À créer
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── api_gateway/
    ├── core/
    ├── forex/
    └── transfers/
```

#### Étape 3: Configurer settings.py

```python
# forex_platform/settings.py

# 1. Ajouter les apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 3rd party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    
    # Apps locales
    'apps.api_gateway',
    'apps.core',
    'apps.forex',
    'apps.transfers',
]

# 2. Ajouter middleware CORS
MIDDLEWARE = [
    # ... existing middleware ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

# 3. Configurer REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# 4. Configurer Swagger/OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Taux de Change',
    'DESCRIPTION': 'API pour consulter et convertir les taux de change',
    'VERSION': '1.0.0',
}

# 5. Configurer Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# 6. Configurer CORS (pour les devs locaux)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

#### Étape 4: Créer celery.py

```python
# forex_platform/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forex_platform.settings')

app = Celery('forex_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

#### Étape 5: Configurer les URLs

```python
# forex_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include('apps.forex.urls')),
    path('api/', include('apps.core.urls')),
    
    # Swagger/OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```

#### Étape 6: Configurer Redis (optionnel pour dev local)

```bash
# Sur Windows: installer Redis
# Option 1: Avec WSL2
wsl
sudo apt-get install redis-server
redis-server

# Option 2: Utiliser un service Docker
docker run -d -p 6379:6379 redis:latest

# Tester la connexion
redis-cli ping
# Résultat: PONG
```

#### Étape 7: Créer un .env.example

```bash
# .env.example
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost/apiexchange

# Redis
REDIS_URL=redis://localhost:6379/0

# Providers
FIXER_API_KEY=your-fixer-key-here

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Étape 8: Tester l'Environnement

```bash
# 1. Faire les migrations
python manage.py makemigrations
python manage.py migrate

# 2. Créer un superuser
python manage.py createsuperuser

# 3. Démarrer Django
python manage.py runserver

# 4. Vérifier Swagger
# Allez sur: http://localhost:8000/api/docs/
# Vous devez voir une page avec "API Taux de Change"

# 5. Démarrer Celery (dans un autre terminal)
celery -A forex_platform worker -l info

# 6. Vérifier que Celery fonctionne
# Vous devez voir:
# [*] Mingle enabled
# [*] Ready to accept tasks
```

### ✅ Checklist d'Implémentation
- [ ] venv créé et activé
- [ ] requirements.txt installés
- [ ] Projet Django créé
- [ ] 4 apps créées
- [ ] settings.py configuré
- [ ] celery.py créé
- [ ] Redis accessible
- [ ] Django runserver fonctionne
- [ ] Swagger accessible sur /api/docs/
- [ ] Celery worker démarre sans erreur

### 🚨 Pièges Courants
- ❌ Redis non installé → Utiliser docker pour tester rapidement
- ❌ INSTALLED_APPS incomplet → Ajouter toutes les apps créées
- ❌ Oublier les migrations → Toujours faire `python manage.py migrate`
- ❌ Celery worker qui crash → Vérifier CELERY_BROKER_URL

---

## 🎯 Tâche 4: Pipeline CI Opérationnel

### 💡 C'est Quoi?
Automatiser les tests et vérifications **à chaque commit**.

### 📝 À Faire

#### Étape 1: Créer un Test Simple

```python
# apps/core/tests.py

from django.test import TestCase
from rest_framework.test import APIClient

class HealthCheckTestCase(TestCase):
    def test_health_endpoint_exists(self):
        client = APIClient()
        response = client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
```

#### Étape 2: Créer le Fichier de Configuration GitHub Actions

```yaml
# .github/workflows/tests.yml

name: CI Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:latest
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run linting
      run: |
        pip install flake8 black isort
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check .
        isort --check-only .
    
    - name: Run migrations
      run: python manage.py migrate
    
    - name: Run tests
      run: python manage.py test
    
    - name: Generate coverage report
      run: |
        pip install coverage
        coverage run --source='.' manage.py test
        coverage report
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
```

#### Étape 3: Configurer le Linting Local

```bash
# Installer les outils de linting
pip install flake8 black isort

# Vérifier la syntaxe
flake8 .

# Formater le code automatiquement
black .
isort .

# Ajouter un pre-commit hook (optionnel)
pip install pre-commit

# Créer .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Installer les hooks
pre-commit install

# Maintenant, chaque commit va faire les vérifications automatiquement
```

### ✅ Checklist d'Implémentation
- [ ] .github/workflows/tests.yml créé
- [ ] Au moins 1 test qui passe
- [ ] Linting configuré (flake8, black, isort)
- [ ] Pipeline CI déclenché sur un push de test
- [ ] Rapport de couverture généré

### 🚨 Pièges Coumons
- ❌ Services (Postgres, Redis) pas démarrés dans CI → Utiliser `services:` dans le workflow
- ❌ Dépendances manquantes dans requirements.txt → Vérifier que tout est listée
- ❌ Migrations pas appliquées avant tests → Ajouter `python manage.py migrate`

---

# SPRINT 2: MODÈLES DE DONNÉES & SYNCHRONISATION

## 🎯 Tâche 5: Schéma DB Finalisé

### 💡 C'est Quoi?
Créer les **modèles Django** qui représentent les données (devises, taux, historique).

### 📝 À Faire - Étape par Étape

#### Étape 1: Concevoir le Schéma (1 jour)

```
Devise (Currency)
├─ code (EUR, USD, GBP) ← unique
├─ name (Euro, US Dollar)
└─ symbol (€, $, £)

Taux de Change (ExchangeRate)
├─ source_currency (FK → Currency)
├─ target_currency (FK → Currency)
├─ rate (1.10)
└─ updated_at

Snapshot Taux (RateSnapshot)
├─ exchange_rate (FK → ExchangeRate)
├─ timestamp
└─ value (1.10)
```

#### Étape 2: Créer les Modèles

```python
# apps/forex/models.py

from django.db import models
from decimal import Decimal

class Currency(models.Model):
    """Représente une devise (EUR, USD, etc.)"""
    
    code = models.CharField(
        max_length=3,
        unique=True,
        db_index=True,
        help_text="Code ISO 4217 (EUR, USD, GBP, etc.)"
    )
    name = models.CharField(
        max_length=255,
        help_text="Nom complet de la devise"
    )
    symbol = models.CharField(
        max_length=10,
        help_text="Symbole de la devise (€, $, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
        verbose_name_plural = "currencies"
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return self.code


class ExchangeRate(models.Model):
    """Représente un taux de change (EUR->USD = 1.10)"""
    
    source_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='exchange_rates_from',
        help_text="Devise de départ (p.ex. EUR)"
    )
    target_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='exchange_rates_to',
        help_text="Devise d'arrivée (p.ex. USD)"
    )
    rate = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        help_text="Taux de change (p.ex. 1.10000000)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Dernière mise à jour"
    )
    
    class Meta:
        unique_together = ('source_currency', 'target_currency')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['source_currency', 'target_currency']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"{self.source_currency.code}/{self.target_currency.code}"


class RateSnapshot(models.Model):
    """Historique des taux de change"""
    
    exchange_rate = models.ForeignKey(
        ExchangeRate,
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Quand ce snapshot a été créé"
    )
    value = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        help_text="Valeur du taux à ce moment"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['exchange_rate', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.exchange_rate} @ {self.timestamp}"
```

#### Étape 3: Créer les Migrations

```bash
# Générer les migrations
python manage.py makemigrations

# Vérifier le fichier généré
cat apps/forex/migrations/0001_initial.py

# Appliquer les migrations
python manage.py migrate

# Vérifier en base de données
python manage.py dbshell
> \dt  (PostgreSQL)
> SHOW TABLES;  (MySQL)
```

#### Étape 4: Tester les Modèles

```python
# apps/forex/tests.py

from django.test import TestCase
from decimal import Decimal
from apps.forex.models import Currency, ExchangeRate, RateSnapshot

class CurrencyModelTest(TestCase):
    """Test le modèle Currency"""
    
    def setUp(self):
        """Créer une devise de test"""
        self.currency = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€'
        )
    
    def test_currency_creation(self):
        """Vérifier qu'une devise peut être créée"""
        self.assertEqual(self.currency.code, 'EUR')
        self.assertEqual(str(self.currency), 'EUR')
    
    def test_currency_code_unique(self):
        """Vérifier que le code est unique"""
        with self.assertRaises(Exception):
            Currency.objects.create(
                code='EUR',  # Duplicate!
                name='Duplicate Euro',
                symbol='€€'
            )
    
    def test_currency_ordering(self):
        """Vérifier l'ordre alphabétique"""
        Currency.objects.create(code='USD', name='Dollar', symbol='$')
        Currency.objects.create(code='GBP', name='Pound', symbol='£')
        
        currencies = Currency.objects.all()
        codes = [c.code for c in currencies]
        self.assertEqual(codes, ['EUR', 'GBP', 'USD'])


class ExchangeRateModelTest(TestCase):
    """Test le modèle ExchangeRate"""
    
    def setUp(self):
        """Créer des devises et un taux de test"""
        self.eur = Currency.objects.create(code='EUR', name='Euro', symbol='€')
        self.usd = Currency.objects.create(code='USD', name='Dollar', symbol='$')
        
        self.rate = ExchangeRate.objects.create(
            source_currency=self.eur,
            target_currency=self.usd,
            rate=Decimal('1.10000000')
        )
    
    def test_exchange_rate_creation(self):
        """Vérifier qu'un taux peut être créé"""
        self.assertEqual(self.rate.rate, Decimal('1.10000000'))
        self.assertEqual(str(self.rate), 'EUR/USD')
    
    def test_exchange_rate_unique(self):
        """Vérifier que la paire source/target est unique"""
        with self.assertRaises(Exception):
            ExchangeRate.objects.create(
                source_currency=self.eur,
                target_currency=self.usd,  # Duplicate pair!
                rate=Decimal('1.15000000')
            )
    
    def test_exchange_rate_update(self):
        """Vérifier qu'un taux peut être mis à jour"""
        self.rate.rate = Decimal('1.12000000')
        self.rate.save()
        
        updated_rate = ExchangeRate.objects.get(id=self.rate.id)
        self.assertEqual(updated_rate.rate, Decimal('1.12000000'))


class RateSnapshotModelTest(TestCase):
    """Test le modèle RateSnapshot"""
    
    def setUp(self):
        """Créer une devise, taux et snapshot"""
        self.eur = Currency.objects.create(code='EUR', name='Euro', symbol='€')
        self.usd = Currency.objects.create(code='USD', name='Dollar', symbol='$')
        
        self.rate = ExchangeRate.objects.create(
            source_currency=self.eur,
            target_currency=self.usd,
            rate=Decimal('1.10000000')
        )
        
        self.snapshot = RateSnapshot.objects.create(
            exchange_rate=self.rate,
            value=Decimal('1.10000000')
        )
    
    def test_snapshot_creation(self):
        """Vérifier qu'un snapshot peut être créé"""
        self.assertEqual(self.snapshot.value, Decimal('1.10000000'))
        self.assertIsNotNone(self.snapshot.timestamp)
    
    def test_snapshot_history(self):
        """Vérifier que l'historique fonctionne"""
        # Créer un nouveau snapshot
        RateSnapshot.objects.create(
            exchange_rate=self.rate,
            value=Decimal('1.12000000')
        )
        
        snapshots = RateSnapshot.objects.filter(exchange_rate=self.rate)
        self.assertEqual(snapshots.count(), 2)
        self.assertEqual(snapshots[0].value, Decimal('1.12000000'))  # Plus récent en premier

# Lancer les tests
# python manage.py test apps.forex.tests
```

### ✅ Checklist d'Implémentation
- [ ] 3 modèles créés (Currency, ExchangeRate, RateSnapshot)
- [ ] Migrations créées et appliquées
- [ ] Tests pour chaque modèle (au moins 3 par modèle)
- [ ] Indexes créés pour les requêtes fréquentes
- [ ] Relations (ForeignKey) bien configurées
- [ ] Tests passent: `python manage.py test`

### 🚨 Pièges Courants
- ❌ Oublier `unique_together` → Permet les doublons accidentels
- ❌ Pas d'indexes → Les requêtes seront lentes
- ❌ Utiliseur `Float` au lieu de `Decimal` → Problèmes de précision monétaire
- ❌ Oublier `on_delete=models.CASCADE` → Erreur à la création de la migration

---

## 🎯 Tâche 6: Données de Test Disponibles

### 💡 C'est Quoi?
Charger automatiquement 10 devises et 20 taux dans la base pour faciliter le développement et les tests.

### 📝 À Faire

#### Étape 1: Créer un Management Command

```python
# apps/forex/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from apps.forex.models import Currency, ExchangeRate
from decimal import Decimal

class Command(BaseCommand):
    help = 'Charge les devises et taux de change de base'
    
    def handle(self, *args, **options):
        self.stdout.write('🌱 Chargement des données de test...')
        
        # Créer les devises
        currencies_data = [
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$'},
            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},
            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'},
            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$'},
        ]
        
        currencies = {}
        for data in currencies_data:
            currency, created = Currency.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name'], 'symbol': data['symbol']}
            )
            currencies[data['code']] = currency
            status = '✓ Created' if created else '- Exists'
            self.stdout.write(f"{status}: {data['code']} - {data['name']}")
        
        # Créer les taux de change (depuis EUR)
        rates_data = [
            ('EUR', 'USD', '1.10'),
            ('EUR', 'GBP', '0.95'),
            ('EUR', 'JPY', '130.50'),
            ('EUR', 'CAD', '1.50'),
            ('EUR', 'AUD', '1.60'),
            ('EUR', 'CHF', '0.92'),
            ('EUR', 'CNY', '7.50'),
            ('EUR', 'INR', '95.00'),
            ('EUR', 'MXN', '18.50'),
            
            # Autres paires (exemple: USD -> autres)
            ('USD', 'EUR', '0.91'),
            ('USD', 'GBP', '0.87'),
            ('USD', 'JPY', '120.00'),
            ('USD', 'CAD', '1.36'),
            ('USD', 'AUD', '1.45'),
            ('USD', 'CHF', '0.84'),
            ('USD', 'CNY', '6.80'),
            ('USD', 'INR', '86.00'),
            ('USD', 'MXN', '16.80'),
            
            # Bonus: GBP -> USD (20 taux)
            ('GBP', 'USD', '1.27'),
        ]
        
        for source_code, target_code, rate_value in rates_data:
            source = currencies[source_code]
            target = currencies[target_code]
            
            exchange_rate, created = ExchangeRate.objects.get_or_create(
                source_currency=source,
                target_currency=target,
                defaults={'rate': Decimal(rate_value)}
            )
            
            status = '✓ Created' if created else '- Exists'
            self.stdout.write(f"{status}: {source_code}/{target_code} = {rate_value}")
        
        # Résumé
        total_currencies = Currency.objects.count()
        total_rates = ExchangeRate.objects.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Données chargées:\n'
            f'   {total_currencies} devises\n'
            f'   {total_rates} taux de change'
        ))
```

#### Étape 2: Créer le Dossier Structure

```bash
# Créer la structure de dossier
mkdir -p apps/forex/management/commands

# Créer les __init__.py
touch apps/forex/management/__init__.py
touch apps/forex/management/commands/__init__.py
```

#### Étape 3: Exécuter le Command

```bash
# Charger les données
python manage.py seed_data

# Résultat attendu:
# 🌱 Chargement des données de test...
# ✓ Created: EUR - Euro
# ✓ Created: USD - US Dollar
# ...
# ✅ Données chargées:
#    10 devises
#    20 taux de change
```

#### Étape 4: Vérifier les Données

```bash
# Accéder au shell Django
python manage.py shell

# Vérifier les devises
>>> from apps.forex.models import Currency, ExchangeRate
>>> Currency.objects.count()
10

# Vérifier les taux
>>> ExchangeRate.objects.count()
20

# Tester une requête
>>> eur_usd = ExchangeRate.objects.get(
...     source_currency__code='EUR',
...     target_currency__code='USD'
... )
>>> print(eur_usd.rate)  # Devrait afficher 1.10000000
```

### ✅ Checklist d'Implémentation
- [ ] Management command créé dans `apps/forex/management/commands/seed_data.py`
- [ ] Dossier `management/commands` avec `__init__.py`
- [ ] 10 devises chargées
- [ ] 20 taux de change chargés
- [ ] Vérification que les données sont en base

### 🚨 Pièges Courants
- ❌ Oublier les `__init__.py` → Django ne trouvera pas le command
- ❌ Utiliser `Float` au lieu de `Decimal` → Erreur de conversion
- ❌ Changer les devises existantes → Utiliser `get_or_create`

---

## 🎯 Tâche 7 & 8: Client Provider + Sync Automatique

### 💡 C'est Quoi?
1. **Client Provider:** Récupérer les taux du provider externe (Fixer.io)
2. **Sync Automatique:** Les récupérer automatiquement chaque jour via Celery

### 📝 À Faire

#### Étape 1: Créer une Interface Abstraite

```python
# apps/forex/providers/__init__.py
# C'est un dossier nouveau

# apps/forex/providers/base.py

from abc import ABC, abstractmethod
from typing import List, Dict

class ExchangeRateProvider(ABC):
    """Interface abstraite pour les providers de taux de change"""
    
    @abstractmethod
    def fetch_rates(self, base_currency: str, target_currencies: List[str]) -> Dict:
        """
        Récupère les taux de change.
        
        Args:
            base_currency: Devise de référence (p.ex. 'EUR')
            target_currencies: Liste des devises cibles (p.ex. ['USD', 'GBP'])
        
        Returns:
            {'rates': {'USD': 1.10, 'GBP': 0.95}}
        
        Raises:
            ProviderError: Si impossible de récupérer les taux
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Vérifie que le provider est accessible"""
        pass
```

#### Étape 2: Implémenter Fixer.io

```python
# apps/forex/providers/fixer_io.py

import requests
import logging
from decimal import Decimal
from typing import List, Dict
from .base import ExchangeRateProvider

logger = logging.getLogger(__name__)

class FixerIOProvider(ExchangeRateProvider):
    """Implémentation du provider Fixer.io"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fixer.io"
        self.timeout = 10
    
    def fetch_rates(self, base_currency: str, target_currencies: List[str]) -> Dict:
        """Récupère les taux depuis Fixer.io"""
        
        try:
            url = f"{self.base_url}/latest"
            params = {
                'access_key': self.api_key,
                'base': base_currency.upper(),
                'symbols': ','.join([c.upper() for c in target_currencies])
            }
            
            logger.info(f"Fetching rates from Fixer.io: {base_currency} -> {target_currencies}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success', False):
                error = data.get('error', {}).get('info', 'Unknown error')
                logger.error(f"Fixer.io error: {error}")
                raise ProviderError(f"Fixer.io error: {error}")
            
            logger.info(f"Successfully fetched {len(data.get('rates', {}))} rates")
            return data
        
        except requests.RequestException as e:
            logger.error(f"Fixer.io request failed: {e}")
            raise ProviderError(f"Failed to fetch rates: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ProviderError(f"Unexpected error: {e}")
    
    def health_check(self) -> bool:
        """Vérifie que Fixer.io est accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/latest",
                params={'access_key': self.api_key},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class ProviderError(Exception):
    """Exception levée quand le provider échoue"""
    pass


def get_provider() -> ExchangeRateProvider:
    """Factory pour obtenir une instance du provider"""
    from django.conf import settings
    
    api_key = settings.FIXER_API_KEY
    return FixerIOProvider(api_key=api_key)
```

#### Étape 3: Créer la Tâche Celery

```python
# apps/forex/tasks.py

from celery import shared_task
from apps.forex.models import Currency, ExchangeRate, RateSnapshot
from apps.forex.providers import get_provider, ProviderError
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sync_exchange_rates(self):
    """
    Synchronise les taux de change depuis le provider.
    
    Cette tâche:
    1. Récupère tous les taux du provider
    2. Met à jour ou crée les ExchangeRate
    3. Crée un RateSnapshot pour l'historique
    4. Loggue les résultats
    
    Retry logic:
    - Essaie 3 fois avant d'échouer
    - Attends 5 minutes entre chaque essai
    - Backoff exponentiel
    """
    
    try:
        logger.info("🔄 Démarrage de la synchronisation des taux...")
        
        # Obtenir le provider
        provider = get_provider()
        
        # Vérifier la santé du provider
        if not provider.health_check():
            raise ProviderError("Provider health check failed")
        
        # Déterminer les devises
        base_currency = 'EUR'  # Devise de référence
        all_currencies = Currency.objects.exclude(code=base_currency)
        target_currencies = [c.code for c in all_currencies]
        
        logger.info(f"Récupération des taux: {base_currency} -> {target_currencies}")
        
        # Récupérer les taux du provider
        data = provider.fetch_rates(base_currency, target_currencies)
        rates = data.get('rates', {})
        
        if not rates:
            logger.warning("Aucun taux reçu du provider")
            return "No rates received"
        
        # Mettre à jour les taux en base de données
        source = Currency.objects.get(code=base_currency)
        updated_count = 0
        
        for target_code, rate_value in rates.items():
            try:
                target = Currency.objects.get(code=target_code)
                
                # Créer ou mettre à jour le taux
                exchange_rate, created = ExchangeRate.objects.update_or_create(
                    source_currency=source,
                    target_currency=target,
                    defaults={'rate': Decimal(str(rate_value))}
                )
                
                # Créer un snapshot pour l'historique
                RateSnapshot.objects.create(
                    exchange_rate=exchange_rate,
                    value=Decimal(str(rate_value))
                )
                
                updated_count += 1
                
                status = "✓ Created" if created else "↻ Updated"
                logger.debug(f"{status}: {base_currency}/{target_code} = {rate_value}")
                
            except Currency.DoesNotExist:
                logger.warning(f"Devise {target_code} not found in DB")
            except Exception as e:
                logger.error(f"Error updating rate {target_code}: {e}")
        
        message = f"✅ Synchronisation réussie: {updated_count} taux mis à jour"
        logger.info(message)
        return message
    
    except ProviderError as e:
        logger.error(f"Provider error: {e}")
        # Retry après 5 minutes
        raise self.retry(exc=e, countdown=300, backoff=2)
    
    except Exception as e:
        logger.error(f"Unexpected error in sync_exchange_rates: {e}")
        # Retry après 10 minutes
        raise self.retry(exc=e, countdown=600, backoff=2)
```

#### Étape 4: Configurer Celery Beat

```python
# forex_platform/settings.py

# Ajouter à la fin:

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'sync-exchange-rates': {
        'task': 'apps.forex.tasks.sync_exchange_rates',
        'schedule': crontab(hour=0, minute=0),  # Chaque jour à minuit UTC
        # Alternative: exécuter chaque 1 heure
        # 'schedule': crontab(minute=0),
    },
}
```

#### Étape 5: Tester Localement

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A forex_platform worker -l info

# Terminal 3: Celery beat (scheduler)
celery -A forex_platform beat -l info

# Terminal 4: Tester la tâche manuellement
python manage.py shell

# Dans le shell:
>>> from apps.forex.tasks import sync_exchange_rates
>>> result = sync_exchange_rates.apply_async()
>>> result.get()  # Attends que la tâche se termine et affiche le résultat
'✅ Synchronisation réussie: 9 taux mis à jour'

# Vérifier les logs:
# Terminal 2 devrait afficher:
# [*] Task apps.forex.tasks.sync_exchange_rates succeeded
```

#### Étape 6: Tester avec un Mock (pour CI/CD)

```python
# apps/forex/tests/test_tasks.py

from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.forex.tasks import sync_exchange_rates
from apps.forex.models import Currency, ExchangeRate, RateSnapshot
from decimal import Decimal

class SyncExchangeRatesTaskTest(TestCase):
    
    def setUp(self):
        """Créer les devises de test"""
        self.eur = Currency.objects.create(code='EUR', name='Euro', symbol='€')
        self.usd = Currency.objects.create(code='USD', name='Dollar', symbol='$')
        self.gbp = Currency.objects.create(code='GBP', name='Pound', symbol='£')
    
    @patch('apps.forex.tasks.get_provider')
    def test_sync_success(self, mock_get_provider):
        """Test que la sync crée les taux correctement"""
        
        # Mock du provider
        mock_provider = MagicMock()
        mock_provider.health_check.return_value = True
        mock_provider.fetch_rates.return_value = {
            'rates': {
                'USD': '1.10',
                'GBP': '0.95'
            }
        }
        mock_get_provider.return_value = mock_provider
        
        # Exécuter la tâche
        result = sync_exchange_rates()
        
        # Vérifications
        self.assertIn('2 taux', result)
        
        # Vérifier les taux en DB
        usd_rate = ExchangeRate.objects.get(
            source_currency__code='EUR',
            target_currency__code='USD'
        )
        self.assertEqual(usd_rate.rate, Decimal('1.10'))
        
        # Vérifier que des snapshots ont été créés
        snapshots = RateSnapshot.objects.filter(exchange_rate=usd_rate)
        self.assertEqual(snapshots.count(), 1)
    
    @patch('apps.forex.tasks.get_provider')
    def test_sync_provider_error(self, mock_get_provider):
        """Test que la tâche retry en cas d'erreur"""
        
        mock_provider = MagicMock()
        mock_provider.health_check.return_value = False
        mock_get_provider.return_value = mock_provider
        
        # La tâche devrait lever une exception
        with self.assertRaises(Exception):
            sync_exchange_rates()
```

### ✅ Checklist d'Implémentation
- [ ] Dossier `apps/forex/providers/` créé
- [ ] `base.py` avec interface abstraite
- [ ] `fixer_io.py` avec implémentation Fixer.io
- [ ] `tasks.py` avec tâche Celery
- [ ] `settings.py` configuré pour Celery Beat
- [ ] Tests créés et passent
- [ ] Tâche testée manuellement avec `apply_async()`

### 🚨 Pièges Courants
- ❌ Oublier `settings.FIXER_API_KEY` → Ajouter dans `.env`
- ❌ Celery beat pas démarré → Lancer dans terminal séparé
- ❌ Import circulaire → Éviter les imports circulaires entre models et tasks
- ❌ Pas de reconnexion à Redis → Celery gère cela automatiquement

---

# SPRINT 3: ENDPOINTS & SÉCURITÉ

## 🎯 Tâche 9: Endpoints Déployés

### 💡 C'est Quoi?
Créer **4 endpoints REST** pour exposer l'API.

### 📝 À Faire

### Étape 1: Créer les Serializers

```python
# apps/forex/serializers.py

from rest_framework import serializers
from apps.forex.models import Currency, ExchangeRate

class CurrencySerializer(serializers.ModelSerializer):
    """Sérialise une devise"""
    
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Sérialise un taux de change avec les devises complètes"""
    
    source_currency = CurrencySerializer(read_only=True)
    target_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = ExchangeRate
        fields = [
            'id',
            'source_currency',
            'target_currency',
            'rate',
            'updated_at'
        ]


class ConvertRequestSerializer(serializers.Serializer):
    """Valide la requête de conversion"""
    
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    
    def validate_from_currency(self, value):
        """Vérifie que la devise existe"""
        if not Currency.objects.filter(code=value.upper()).exists():
            raise serializers.ValidationError(
                f"Devise '{value}' inconnue"
            )
        return value.upper()
    
    def validate_to_currency(self, value):
        """Vérifie que la devise existe"""
        if not Currency.objects.filter(code=value.upper()).exists():
            raise serializers.ValidationError(
                f"Devise '{value}' inconnue"
            )
        return value.upper()
    
    def validate_amount(self, value):
        """Vérifie que le montant est positif"""
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être > 0")
        return value


class ConvertResponseSerializer(serializers.Serializer):
    """Sérialise la réponse de conversion"""
    
    from_currency = serializers.CharField()
    to_currency = serializers.CharField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    rate = serializers.DecimalField(max_digits=18, decimal_places=8)
    timestamp = serializers.DateTimeField()
```

### Étape 2: Créer les ViewSets

```python
# apps/forex/views.py

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
import logging

from apps.forex.models import Currency, ExchangeRate
from apps.forex.serializers import (
    CurrencySerializer,
    ExchangeRateSerializer,
    ConvertRequestSerializer,
    ConvertResponseSerializer
)

logger = logging.getLogger(__name__)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint pour lister les devises.
    
    GET /api/currencies/ - Liste toutes les devises
    GET /api/currencies/{id}/ - Détail d'une devise
    """
    
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """Liste toutes les devises disponibles"""
        logger.info("Currency list requested")
        return super().list(request, *args, **kwargs)


class ExchangeRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint pour lister les taux de change.
    
    GET /api/rates/ - Liste tous les taux
    GET /api/rates/{id}/ - Détail d'un taux
    """
    
    queryset = ExchangeRate.objects.select_related(
        'source_currency',
        'target_currency'
    ).all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """Liste tous les taux de change disponibles"""
        logger.info("Exchange rates list requested")
        return super().list(request, *args, **kwargs)


@api_view(['POST'])
def convert_currency(request):
    """
    Convertit un montant d'une devise à une autre.
    
    POST /api/convert/
    {
        "from_currency": "EUR",
        "to_currency": "USD",
        "amount": 100.00
    }
    
    Réponse:
    {
        "from_currency": "EUR",
        "to_currency": "USD",
        "amount": 100.00,
        "converted_amount": 110.00,
        "rate": 1.10000000,
        "timestamp": "2026-05-07T10:00:00Z"
    }
    """
    
    # Valider les entrées
    serializer = ConvertRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Convert request validation failed: {serializer.errors}")
        return Response(
            {'error': 'Invalid parameters', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Récupérer les données validées
        from_code = serializer.validated_data['from_currency']
        to_code = serializer.validated_data['to_currency']
        amount = serializer.validated_data['amount']
        
        logger.info(f"Converting {amount} {from_code} to {to_code}")
        
        # Vérifier qu'on ne convertit pas une devise en elle-même
        if from_code == to_code:
            response_data = {
                'from_currency': from_code,
                'to_currency': to_code,
                'amount': amount,
                'converted_amount': amount,
                'rate': Decimal('1.00000000'),
                'timestamp': datetime.now()
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        # Récupérer le taux de change
        exchange_rate = ExchangeRate.objects.select_related(
            'source_currency',
            'target_currency'
        ).get(
            source_currency__code=from_code,
            target_currency__code=to_code
        )
        
        # Calculer le montant converti
        from decimal import Decimal
        converted_amount = amount * exchange_rate.rate
        
        # Construire la réponse
        response_data = {
            'from_currency': from_code,
            'to_currency': to_code,
            'amount': amount,
            'converted_amount': converted_amount,
            'rate': exchange_rate.rate,
            'timestamp': exchange_rate.updated_at
        }
        
        # Valider la réponse
        response_serializer = ConvertResponseSerializer(response_data)
        
        logger.info(f"Conversion successful: {amount}{from_code} = {converted_amount}{to_code}")
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    except ExchangeRate.DoesNotExist:
        logger.warning(f"Exchange rate not found: {from_code}/{to_code}")
        return Response(
            {'error': f'Exchange rate {from_code}/{to_code} not available'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Currency.DoesNotExist:
        logger.warning(f"Currency not found")
        return Response(
            {'error': 'Currency not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Unexpected error in convert_currency: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """
    Vérifie que l'API est en bonne santé.
    
    GET /api/health/
    
    Réponse:
    {
        "status": "healthy",
        "timestamp": "2026-05-07T10:00:00Z",
        "version": "1.0.0"
    }
    """
    
    from django.utils.timezone import now
    
    try:
        # Vérifier que la DB est accessible
        Currency.objects.count()
        
        response = {
            'status': 'healthy',
            'timestamp': now().isoformat(),
            'version': '1.0.0'
        }
        
        return Response(response, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Response(
            {'status': 'unhealthy', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### Étape 3: Créer les URLs

```python
# apps/forex/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.forex.views import (
    CurrencyViewSet,
    ExchangeRateViewSet,
    convert_currency,
    health_check
)

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'rates', ExchangeRateViewSet, basename='exchange-rate')

urlpatterns = [
    # APIs auto-générées par le router
    path('', include(router.urls)),
    
    # APIs custom
    path('convert/', convert_currency, name='convert'),
    path('health/', health_check, name='health'),
]
```

### Étape 4: Inclure dans les URLs principales

```python
# forex_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include('apps.forex.urls')),
    
    # Swagger/OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### Étape 5: Tester les Endpoints

```bash
# Démarrer le serveur
python manage.py runserver

# Test avec curl (sans auth d'abord, on va la ajouter)
curl http://localhost:8000/api/health/

# Résultat attendu:
# {
#   "status": "healthy",
#   "timestamp": "2026-05-07T10:00:00Z",
#   "version": "1.0.0"
# }
```

### Étape 6: Tests Automatisés

```python
# apps/forex/tests/test_views.py

from django.test import TestCase
from rest_framework.test import APIClient
from apps.forex.models import Currency, ExchangeRate
from decimal import Decimal

class CurrencyAPITest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.eur = Currency.objects.create(code='EUR', name='Euro', symbol='€')
        self.usd = Currency.objects.create(code='USD', name='Dollar', symbol='$')
    
    def test_list_currencies(self):
        """Test GET /api/currencies/"""
        response = self.client.get('/api/currencies/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_currency_detail(self):
        """Test GET /api/currencies/{id}/"""
        response = self.client.get(f'/api/currencies/{self.eur.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'EUR')


class ConvertAPITest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.eur = Currency.objects.create(code='EUR', name='Euro', symbol='€')
        self.usd = Currency.objects.create(code='USD', name='Dollar', symbol='$')
        
        self.rate = ExchangeRate.objects.create(
            source_currency=self.eur,
            target_currency=self.usd,
            rate=Decimal('1.10')
        )
    
    def test_convert_success(self):
        """Test POST /api/convert/ avec montant valide"""
        response = self.client.post('/api/convert/', {
            'from_currency': 'EUR',
            'to_currency': 'USD',
            'amount': '100.00'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['from_currency'], 'EUR')
        self.assertEqual(response.data['converted_amount'], Decimal('110.00'))
    
    def test_convert_invalid_currency(self):
        """Test POST /api/convert/ avec devise inconnue"""
        response = self.client.post('/api/convert/', {
            'from_currency': 'XYZ',
            'to_currency': 'USD',
            'amount': '100.00'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
    
    def test_convert_same_currency(self):
        """Test POST /api/convert/ EUR -> EUR"""
        response = self.client.post('/api/convert/', {
            'from_currency': 'EUR',
            'to_currency': 'EUR',
            'amount': '100.00'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['converted_amount'], Decimal('100.00'))
        self.assertEqual(response.data['rate'], Decimal('1.00000000'))


class HealthCheckTest(TestCase):
    
    def test_health_check(self):
        """Test GET /api/health/"""
        response = self.client.get('/api/health/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('timestamp', response.data)
```

### ✅ Checklist d'Implémentation
- [ ] 4 serializers créés
- [ ] 2 ViewSets créés (Currency, ExchangeRate)
- [ ] 2 API views créées (convert, health)
- [ ] URLs configurées dans `apps/forex/urls.py`
- [ ] Swagger accessible sur `/api/docs/`
- [ ] Tests pour chaque endpoint
- [ ] Tous les tests passent

---

*Le document continue de la même façon pour les tâches 10-19...*

---

# 🎓 RESSOURCES UTILES

## Documentation Officielle
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [drf-spectacular (Swagger)](https://drf-spectacular.readthedocs.io/)

## Tutoriels YouTube Recommandés
- Django REST Framework: Full Course
- Celery with Django: Complete Guide
- PostgreSQL with Django

## Articles Utiles
- [Django Models Best Practices](https://www.realpython.com/django-models/)
- [Building APIs with DRF](https://testdriven.io/blog/drf-intro/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html)

---

# 🐛 DEBUGGING TIPS

## Logs
```bash
# Voir tous les logs
python manage.py runserver --debug

# Logs détaillés Celery
celery -A forex_platform worker -l debug
```

## Shell Django
```bash
# Accéder au shell interactive
python manage.py shell

# Teste tes modèles
>>> from apps.forex.models import Currency
>>> Currency.objects.count()
10
```

## Tests
```bash
# Exécuter tous les tests
python manage.py test

# Exécuter les tests d'une app
python manage.py test apps.forex

# Tests avec verbose
python manage.py test --verbosity=2

# Tests avec coverage
coverage run --source='.' manage.py test
coverage report
```

---

**Document créé:** 7 mai 2026  
**Version:** 1.0  
**Pour questions:** Contactez le Tech Lead
