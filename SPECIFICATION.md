# 📋 Cahier des Charges — Spécification Fonctionnelle Complète
# ForexPlatform API — Service de Taux de Change International

> **Version** : 1.0.0
> **Date** : Mai 2026
> **Auteur** : WIB (World International Business)
> **Stack** : Python 3.11 · Django 4.2 · PostgreSQL · Redis · Celery · Docker

---

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Objectifs](#2-objectifs)
3. [Architecture technique](#3-architecture-technique)
4. [Modules fonctionnels](#4-modules-fonctionnels)
5. [Modèles de données](#5-modèles-de-données)
6. [Endpoints API — Référence complète](#6-endpoints-api--référence-complète)
7. [Format des réponses](#7-format-des-réponses)
8. [Sécurité et Authentification](#8-sécurité-et-authentification)
9. [Tiers tarifaires et Spread](#9-tiers-tarifaires-et-spread)
10. [Providers Forex](#10-providers-forex)
11. [Tâches automatiques Celery](#11-tâches-automatiques-celery)
12. [Interface de test](#12-interface-de-test)
13. [Infrastructure Docker](#13-infrastructure-docker)
14. [Variables d'environnement](#14-variables-denvironnement)
15. [État d'avancement](#15-état-davancement)
16. [Roadmap](#16-roadmap)

---

## 1. Présentation du projet

**ForexPlatform** est une **API REST professionnelle** développée en Python/Django,
conçue pour alimenter une application mobile de conversion et transfert de devises
internationales. Elle s'inspire des services leaders du marché :

| Service    | Fonctionnalité reprise                              |
|------------|-----------------------------------------------------|
| XE.com     | Taux de change en temps réel, multi-devises         |
| Wise       | Taux transparents, spread visible, tiers tarifaires |
| Revolut    | Wallets multi-devises, transferts instantanés       |
| Remitly    | Transferts internationaux avec suivi                |

Le projet est **API-first** : aucune interface utilisateur côté serveur. Tout est
conçu pour être consommé par une app mobile (Flutter, React Native, iOS, Android).

---

## 2. Objectifs

### Objectifs fonctionnels

- Récupérer les taux de change en temps réel depuis plusieurs sources externes
- Agréger et normaliser ces taux pour produire un taux de marché fiable
- Appliquer un spread et une marge commerciale pour produire un taux business
- Exposer une API REST sécurisée consommable par l'app mobile
- Gérer des portefeuilles (wallets) multi-devises par utilisateur
- Traiter des transferts internationaux avec comptabilité double-entrée
- Stocker l'historique des taux (snapshots OHLC quotidiens)

### Objectifs non-fonctionnels

- **Haute disponibilité** : cache Redis, retry automatique des providers
- **Performance** : réponse < 100ms grâce au cache
- **Sécurité** : JWT, API Keys hashées, rate limiting, audit logs
- **Scalabilité** : architecture microservices via Docker
- **Maintenabilité** : code modulaire, documenté, OpenAPI

---

## 3. Architecture technique

```
┌─────────────────────────────────────────────────────────────┐
│              Application Mobile (Flutter / RN)              │
│                    HTTPS · JWT · API Key                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   NGINX (Reverse Proxy)                     │
│           Rate Limiting · SSL/TLS · Security Headers        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Django 4.2 + DRF (Gunicorn)                    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ API Gateway │  │  Forex App  │  │  Transfers App   │    │
│  │ Auth · Keys │  │  Rates · Fx │  │  Wallets · Txfr  │    │
│  │ Throttle    │  │  Aggregator │  │  Ledger          │    │
│  │ Audit Logs  │  │  RateEngine │  │                  │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
└────────┬──────────────────┬─────────────────────────────────┘
         │                  │
┌────────▼──────┐  ┌────────▼──────────────────────────────┐
│  PostgreSQL   │  │  Redis (Cache + Sessions + Results)   │
└───────────────┘  └───────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              RabbitMQ + Celery Workers                      │
│       Sync toutes les 5min · Archive quotidienne            │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
    ┌────▼─────┐    ┌──────▼──────┐  ┌───────▼────────┐
    │ Fixer.io │    │ OXR / ECB   │  │ ExchangeRate-  │
    │  (paid)  │    │ (free/paid) │  │    API (free)  │
    └──────────┘    └─────────────┘  └────────────────┘
```

### Stack technologique

| Couche         | Technologie              | Rôle                        |
|----------------|--------------------------|-----------------------------|
| Langage        | Python 3.11              | —                           |
| Framework      | Django 4.2               | ORM, Admin, Auth            |
| API            | Django REST Framework    | Sérialisation, Vues, Auth   |
| Base de données| PostgreSQL 15            | Données persistantes        |
| Cache          | Redis 7                  | Taux, sessions, throttling  |
| File de tâches | RabbitMQ + Celery        | Sync asynchrone             |
| Auth           | SimpleJWT                | Tokens JWT                  |
| Proxy          | Nginx                    | SSL, rate limiting          |
| Serveur        | Gunicorn                 | WSGI production             |
| Conteneurs     | Docker + Compose         | Déploiement                 |
| Docs API       | drf-spectacular          | Swagger / OpenAPI 3         |

---

## 4. Modules fonctionnels

### 4.1 Module Core — apps/core

Gère les données de référence de base.

- **33 devises** internationales pré-chargées (USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY…)
- Code ISO 4217, nom, symbole, drapeau emoji
- Champ `is_active` pour activer/désactiver une devise

### 4.2 Module Forex Aggregator — apps/forex/aggregator.py

Orchestre la récupération des taux depuis 4 providers en **parallèle**.

Processus d'agrégation :
```
1. FETCH      → Appel HTTP concurrent aux 4 providers
2. NORMALIZE  → Rebase tous les taux en USD (pivot)
3. FILTER     → Écarte les taux aberrants (seuil ±20%)
4. AGGREGATE  → Moyenne pondérée selon fiabilité du provider
5. PERSIST    → Sauvegarde en base + invalidation cache
6. STATS      → Mise à jour compteurs succès/erreur providers
```

Détection d'anomalies :
- Calcule la médiane de tous les providers pour une devise
- Écarte tout provider dont le taux dévie de plus de 20% de la médiane
- Configurable via `FOREX_ANOMALY_THRESHOLD` dans `.env`

### 4.3 Module Rate Engine — apps/forex/rate_engine.py

- **Taux marché** : taux brut issu de l'agrégation multi-providers
- **Taux business** : taux marché × (1 + spread + marge) selon le tier
- **Taux croisés** : EUR/GBP calculé via pivot USD si direct indisponible
- **Cache Redis** : TTL 300s, invalidation automatique à chaque sync

```
Taux business = Taux marché × (1 + spread + marge)
Montant converti = montant × taux business
Frais = montant × spread × taux business
```

### 4.4 Module API Gateway — apps/api_gateway

- Authentification JWT + API Key sur chaque requête
- Rate limiting sliding window par tier
- Audit log de chaque requête (méthode, path, status, IP, temps réponse)
- API Keys : préfixe `fxp_`, hash SHA-256 en base, affichée une seule fois

### 4.5 Module Transfers — apps/transfers

- **Wallet** : un portefeuille par (utilisateur, devise), opérations atomiques
- **Transaction** : grand livre comptable immuable avec `balance_before/after`
- **Transfer** : débit + crédit atomiques, référence cryptographique unique

---

## 5. Modèles de données

```
Currency
  code            PK CharField (ISO 4217 : "USD", "EUR"…)
  name            CharField
  symbol          CharField
  flag            CharField (emoji)
  is_active       BooleanField

ForexProvider
  name            CharField
  code            CharField unique
  is_active       BooleanField
  is_free         BooleanField
  weight          FloatField (pondération agrégation)
  priority        IntegerField
  success_count   PositiveIntegerField
  error_count     PositiveIntegerField
  last_sync_at    DateTimeField

ExchangeRate
  from_currency   FK(Currency)
  to_currency     FK(Currency)
  market_rate     DecimalField(20,8)
  business_rate   DecimalField(20,8)
  spread          DecimalField(6,4)
  margin          DecimalField(6,4)
  sources         JSONField (liste des providers)
  fetched_at      DateTimeField
  is_stale        BooleanField

RateHistory  (snapshot OHLC quotidien)
  from_currency   FK(Currency)
  to_currency     FK(Currency)
  date            DateField
  open_rate       DecimalField(20,8)
  high_rate       DecimalField(20,8)
  low_rate        DecimalField(20,8)
  close_rate      DecimalField(20,8)
  avg_rate        DecimalField(20,8)
  data_points     IntegerField

APIClient
  user            FK(User)
  name            CharField
  api_key_prefix  CharField (8 chars pour affichage)
  api_key_hash    CharField(64) unique (SHA-256)
  tier            CharField (free / standard / premium / partner)
  quota_requests_per_hour  PositiveIntegerField
  total_requests  PositiveBigIntegerField
  expires_at      DateTimeField nullable
  is_active       BooleanField

AuditLog
  api_client      FK(APIClient) nullable
  user            FK(User) nullable
  method          CharField
  path            CharField
  status_code     PositiveSmallIntegerField
  ip_address      GenericIPAddressField
  response_time_ms PositiveIntegerField
  timestamp       DateTimeField (indexé)

Wallet
  id              UUIDField PK
  user            FK(User)
  currency        FK(Currency)
  balance         DecimalField(20,4)
  reserved_balance DecimalField(20,4)
  is_active       BooleanField

Transaction
  id              UUIDField PK
  wallet          FK(Wallet)
  transaction_type CharField (credit / debit / reserve / release / fee)
  amount          DecimalField(20,4)
  balance_before  DecimalField(20,4)
  balance_after   DecimalField(20,4)
  status          CharField (pending / completed / failed / reversed)
  reference       CharField (indexé)
  created_at      DateTimeField (indexé)

Transfer
  id              UUIDField PK
  reference       CharField unique ("TXFxxxxxxxxxx")
  sender          FK(User)
  recipient       FK(User)
  sender_wallet   FK(Wallet)
  recipient_wallet FK(Wallet)
  source_amount   DecimalField(20,4)
  source_currency FK(Currency)
  destination_amount DecimalField(20,4)
  destination_currency FK(Currency)
  market_rate     DecimalField(20,8)
  applied_rate    DecimalField(20,8)
  spread_pct      DecimalField(6,4)
  fee_amount      DecimalField(20,4)
  tier            CharField
  status          CharField (initiated / pending / processing / completed / failed)
  sender_transaction   OneToOne(Transaction)
  recipient_transaction OneToOne(Transaction)
  initiated_at    DateTimeField
  completed_at    DateTimeField nullable
```

---

## 6. Endpoints API — Référence complète

### Base URL
```
Développement : http://localhost/api/v1/
Production    : https://votre-domaine.com/api/v1/
```

---

### Authentification

```
POST  /api/v1/auth/token/
      Body : { "username": "...", "password": "..." }
      Auth : Non requis
      Retour : { "access": "eyJ...", "refresh": "eyJ..." }

POST  /api/v1/auth/token/refresh/
      Body : { "refresh": "eyJ..." }
      Auth : Non requis
      Retour : { "access": "eyJ..." }

POST  /api/v1/auth/token/blacklist/
      Body : { "refresh": "eyJ..." }
      Auth : JWT
      Retour : 205 No Content (logout)
```

---

### Devises

```
GET   /api/v1/currencies/
      Auth : Non requis
      Retour :
      {
        "success": true,
        "count": 33,
        "currencies": [
          { "code": "USD", "name": "US Dollar", "symbol": "$", "flag": "🇺🇸" },
          { "code": "EUR", "name": "Euro",       "symbol": "€", "flag": "🇪🇺" },
          ...
        ]
      }
```

---

### Taux de change

```
GET   /api/v1/rates/
GET   /api/v1/rates/?base=EUR
      Auth : JWT ou API Key
      Paramètre : base (défaut USD)
      Retour :
      {
        "success": true,
        "source": "cache",
        "base": "USD",
        "count": 32,
        "timestamp": "2026-05-06T09:00:00Z",
        "rates": {
          "EUR": {
            "market_rate": "0.92150000",
            "business_rate": "0.90767800",
            "spread": "0.0150",
            "fetched_at": "2026-05-06T09:00:00Z",
            "is_stale": false
          },
          "GBP": { ... }
        }
      }

GET   /api/v1/rates/USD/EUR/
      Auth : JWT ou API Key
      Retour :
      {
        "success": true,
        "rate": {
          "pair": "USDEUR",
          "from_currency": "USD",
          "to_currency": "EUR",
          "market_rate": "0.92150000",
          "business_rate": "0.90767800",
          "spread": "0.0150",
          "fetched_at": "2026-05-06T09:00:00Z",
          "is_stale": false
        }
      }
```

---

### Conversion

```
POST  /api/v1/convert/
      Auth : JWT ou API Key
      Body :
      {
        "from_currency": "USD",
        "to_currency": "EUR",
        "amount": 500.00,
        "tier": "standard"
      }
      Retour :
      {
        "success": true,
        "conversion": {
          "from_currency": "USD",
          "to_currency": "EUR",
          "amount": "500.00",
          "converted_amount": "453.84",
          "market_rate": "0.92150000",
          "business_rate": "0.90767800",
          "spread_pct": "1.50",
          "fee_amount": "6.91",
          "tier": "standard",
          "timestamp": "2026-05-06T09:00:00Z"
        }
      }
```

---

### Historique des taux (OHLC)

```
GET   /api/v1/history/USD/EUR/
GET   /api/v1/history/USD/EUR/?days=7
GET   /api/v1/history/USD/EUR/?days=365
      Auth : JWT ou API Key
      Paramètre : days (défaut 30, max 365)
      Retour :
      {
        "success": true,
        "from_currency": "USD",
        "to_currency": "EUR",
        "count": 30,
        "history": [
          {
            "date": "2026-05-05",
            "open_rate":  "0.921200",
            "high_rate":  "0.923400",
            "low_rate":   "0.919800",
            "close_rate": "0.921500",
            "avg_rate":   "0.921475",
            "data_points": 288
          }
        ]
      }
```

---

### Santé

```
GET   /api/v1/health/
      Auth : Non requis (public)
      Retour :
      {
        "status": "ok",
        "service": "ForexPlatform API",
        "version": "1.0.0",
        "timestamp": "2026-05-06T09:00:00Z",
        "checks": {
          "database": "ok",
          "cache": "ok"
        }
      }
```

---

### Stats et Administration (Admin uniquement)

```
GET   /api/v1/forex/stats/
      Auth : JWT Admin
      Retour :
      {
        "success": true,
        "stats": {
          "total_currencies": 33,
          "total_pairs": 32,
          "active_providers": 4,
          "last_sync": "2026-05-06T09:00:00Z",
          "stale_pairs": 0
        }
      }

GET   /api/v1/forex/providers/
      Auth : JWT Admin
      Retour : liste des providers avec stats de santé

POST  /api/v1/forex/sync/
      Auth : JWT Admin
      Retour : { "success": true, "task_id": "uuid" }
```

---

### Wallets

```
GET   /api/v1/wallets/
      Auth : JWT
      Retour :
      {
        "success": true,
        "wallets": [
          {
            "id": "uuid",
            "currency": { "code": "USD", "name": "US Dollar", "symbol": "$" },
            "balance": "1250.0000",
            "reserved_balance": "0.0000",
            "available_balance": "1250.0000",
            "is_active": true
          }
        ]
      }

POST  /api/v1/wallets/
      Auth : JWT
      Body : { "currency_code": "EUR" }
      Retour : { "success": true, "created": true, "wallet": { ... } }

GET   /api/v1/wallets/EUR/transactions/
      Auth : JWT
      Retour : liste paginée des transactions du wallet EUR
```

---

### Transferts internationaux

```
POST  /api/v1/transfers/
      Auth : JWT
      Body :
      {
        "recipient_id": 42,
        "source_currency": "USD",
        "destination_currency": "EUR",
        "amount": 200.00
      }
      Retour :
      {
        "success": true,
        "transfer": {
          "reference": "TXF3KJ8MN2PQ",
          "source_amount": "200.0000",
          "source_currency": "USD",
          "destination_amount": "181.54",
          "destination_currency": "EUR",
          "market_rate": "0.92150000",
          "applied_rate": "0.90767800",
          "spread_pct": "0.0150",
          "fee_amount": "2.76",
          "status": "completed",
          "initiated_at": "2026-05-06T09:00:00Z",
          "completed_at": "2026-05-06T09:00:01Z"
        }
      }

GET   /api/v1/transfers/
      Auth : JWT
      Retour : historique de tous mes transferts

GET   /api/v1/transfers/TXF3KJ8MN2PQ/
      Auth : JWT
      Retour : détail d'un transfert par sa référence
```

---

### Clés API

```
GET   /api/v1/api-keys/
      Auth : JWT
      Retour : liste de mes clés API

POST  /api/v1/api-keys/create/
      Auth : JWT
      Body : { "name": "Mon App Mobile", "tier": "standard" }
      Retour : { "raw_key": "fxp_xxxx..." }  ← affiché UNE SEULE FOIS

DELETE /api/v1/api-keys/<id>/
      Auth : JWT
      Retour : 204 No Content
```

---

## 7. Format des réponses

### Succès
```json
{ "success": true, "data": { ... } }
```

### Erreur
```json
{ "success": false, "error": "Message lisible" }
```

### Codes HTTP

| Code | Signification        | Quand                              |
|------|----------------------|------------------------------------|
| 200  | OK                   | Requête réussie                    |
| 201  | Created              | Ressource créée (wallet, transfer) |
| 400  | Bad Request          | Données invalides                  |
| 401  | Unauthorized         | Token manquant ou expiré           |
| 403  | Forbidden            | Accès refusé (endpoint admin)      |
| 404  | Not Found            | Paire de devises inconnue          |
| 422  | Unprocessable Entity | Fonds insuffisants                 |
| 429  | Too Many Requests    | Quota dépassé                      |
| 503  | Service Unavailable  | Taux temporairement indisponibles  |

---

## 8. Sécurité et Authentification

### JWT (JSON Web Token)

```
Header : Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

| Token         | Durée   | Usage                              |
|---------------|---------|------------------------------------|
| Access Token  | 1 heure | Authentifier les requêtes API      |
| Refresh Token | 7 jours | Obtenir un nouvel access token     |

Flux d'authentification côté app mobile :
```
1. POST /auth/token/           → stocker access + refresh en mémoire sécurisée
2. Requêtes API                → envoyer access dans le header Authorization
3. Si erreur 401 reçue         → POST /auth/token/refresh/
4. Si refresh expiré           → rediriger vers l'écran de login
5. Logout                      → POST /auth/token/blacklist/
```

### API Key

```
Header : X-API-Key: fxp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- Préfixe `fxp_` + token aléatoire 32 octets (URL-safe)
- Seul le **hash SHA-256** est stocké en base (jamais la clé brute)
- La clé brute est affichée **une seule fois** à la création
- Expiration optionnelle, quotas personnalisables par client

### Rate Limiting (Sliding Window — 1 heure)

| Tier     | Limite      | Spread appliqué |
|----------|-------------|-----------------|
| Anonyme  | 20 req/h    | —               |
| Free     | 100 req/h   | 2.5%            |
| Standard | 1 000 req/h | 1.5%            |
| Premium  | 5 000 req/h | 0.8%            |
| Partner  | 50 000 req/h| 0.3%            |

### Autres mesures de sécurité

- Headers Nginx : `X-Frame-Options`, `X-Content-Type-Options`, `HSTS`
- CORS configuré (origines autorisées uniquement)
- Audit log de chaque requête (IP, user-agent, temps de réponse)
- Pas de SQL brut (ORM Django uniquement)
- Secrets via variables d'environnement uniquement

---

## 9. Tiers tarifaires et Spread

Le spread est la différence entre le taux marché (brut) et le taux business
(appliqué à l'utilisateur). C'est la source de revenu de la plateforme.

```
Taux business = Taux marché × (1 + spread + marge)
```

| Tier     | Spread | Marge | Exemple : marché USD/EUR = 0.9215 |
|----------|--------|-------|-----------------------------------|
| Free     | 2.5%   | 0.5%  | Taux appliqué → 0.8935            |
| Standard | 1.5%   | 0.3%  | Taux appliqué → 0.9032            |
| Premium  | 0.8%   | 0.2%  | Taux appliqué → 0.9122            |
| Partner  | 0.3%   | 0.1%  | Taux appliqué → 0.9178            |

---

## 10. Providers Forex

| Provider                   | Type     | Clé requise               | Fréquence  | Fiabilité |
|----------------------------|----------|---------------------------|------------|-----------|
| Fixer.io                   | Payant   | `FIXER_API_KEY`           | Temps réel | ★★★★★     |
| Open Exchange Rates (OXR)  | Freemium | `OPENEXCHANGERATES_APP_ID`| Horaire    | ★★★★☆     |
| ExchangeRate-API           | Freemium | `EXCHANGERATE_API_KEY`    | Quotidien  | ★★★☆☆     |
| ECB (Banque Centrale Eur.) | Gratuit  | Aucune clé requise        | Quotidien  | ★★★★☆     |

### Où obtenir les clés (plans gratuits disponibles)

- **Open Exchange Rates** (free, base USD) :
  https://openexchangerates.org/signup/free

- **ExchangeRate-API** (free, 1500 req/mois) :
  https://www.exchangerate-api.com

- **ECB** : aucune inscription, données publiques XML :
  https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml

- **Fixer.io** (payant, le plus complet) :
  https://fixer.io/product

---

## 11. Tâches automatiques Celery

| Tâche                    | Fréquence            | Description                              |
|--------------------------|----------------------|------------------------------------------|
| `sync_all_rates`         | Toutes les 5 min     | Sync principale depuis tous les providers|
| `full_rate_refresh`      | Toutes les heures    | Refresh + marquage des taux périmés      |
| `archive_daily_rates`    | 00:05 UTC chaque jour| Snapshot OHLC quotidien dans RateHistory |
| `cleanup_old_rate_history`| Chaque dimanche     | Suppression historiques > 365 jours      |
| `check_providers_health` | Toutes les 30 min    | Ping providers + mise à jour des stats   |

---

## 12. Interface de test

### Swagger UI (recommandé)

```
URL : http://localhost/api/docs/
```

Interface graphique complète pour tester chaque endpoint directement dans
le navigateur. Supporte l'authentification JWT (bouton "Authorize").

### ReDoc

```
URL : http://localhost/api/redoc/
```

Documentation lisible et exportable. Idéal pour partager avec les
développeurs de l'app mobile.

### Postman / Insomnia

1. Ouvrir Postman
2. `Import` → `Link`
3. Coller : `http://localhost/api/schema/`
4. La collection complète est générée automatiquement

### Flux de test recommandé (étape par étape)

```
Étape 1 — Vérifier la santé
  GET http://localhost/api/v1/health/
  (aucune auth requise)

Étape 2 — S'authentifier
  POST http://localhost/api/v1/auth/token/
  Body : { "username": "WIB", "password": "homeboY2026" }
  → Copier le champ "access" de la réponse

Étape 3 — Voir les devises disponibles
  GET http://localhost/api/v1/currencies/
  Header : Authorization: Bearer <access_token>

Étape 4 — Consulter tous les taux
  GET http://localhost/api/v1/rates/?base=USD
  Header : Authorization: Bearer <access_token>

Étape 5 — Taux d'une paire précise
  GET http://localhost/api/v1/rates/USD/EUR/
  Header : Authorization: Bearer <access_token>

Étape 6 — Faire une conversion
  POST http://localhost/api/v1/convert/
  Header : Authorization: Bearer <access_token>
  Body : { "from_currency": "USD", "to_currency": "EUR", "amount": 100 }

Étape 7 — Voir l'historique
  GET http://localhost/api/v1/history/USD/EUR/?days=7
  Header : Authorization: Bearer <access_token>

Étape 8 — Créer un wallet EUR
  POST http://localhost/api/v1/wallets/
  Header : Authorization: Bearer <access_token>
  Body : { "currency_code": "EUR" }

Étape 9 — Créer une clé API
  POST http://localhost/api/v1/api-keys/create/
  Header : Authorization: Bearer <access_token>
  Body : { "name": "Mon App Mobile", "tier": "standard" }
  → Sauvegarder la "raw_key" (affichée une seule fois)
```

---

## 13. Infrastructure Docker

### Services

| Service          | Image                    | Port(s)      | Rôle                      |
|------------------|--------------------------|--------------|---------------------------|
| `nginx`          | nginx:alpine             | 80, 443      | Reverse proxy, SSL        |
| `app`            | Dockerfile local         | —            | Django + Gunicorn         |
| `db`             | postgres:15              | 5432         | Base de données           |
| `redis`          | redis:7-alpine           | 6379         | Cache + sessions          |
| `rabbitmq`       | rabbitmq:3-management    | 5672, 15672  | Message broker            |
| `celery_worker`  | Dockerfile local         | —            | Exécution des tâches      |
| `celery_beat`    | Dockerfile local         | —            | Planificateur             |
| `flower`         | Dockerfile local         | 5555         | Monitoring Celery         |

### Commandes essentielles

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs de l'API
docker-compose logs -f app

# Voir les logs Celery
docker-compose logs -f celery_worker

# Forcer une migration
docker-compose exec app python manage.py migrate

# Créer un superuser
docker-compose exec app python manage.py createsuperuser
```

### Interfaces disponibles

| Interface       | URL                          | Credentials         |
|-----------------|------------------------------|---------------------|
| API REST        | http://localhost/api/v1/     | JWT / API Key       |
| Swagger UI      | http://localhost/api/docs/   | —                   |
| ReDoc           | http://localhost/api/redoc/  | —                   |
| Django Admin    | http://localhost/admin/      | WIB / homeboY2026   |
| Flower (Celery) | http://localhost:5555        | —                   |
| RabbitMQ UI     | http://localhost:15672       | guest / guest       |

---

## 14. Variables d'environnement

Fichier `.env` à la racine du projet :

```env
# === APPLICATION ===
SECRET_KEY=votre-secret-key-django-tres-longue-et-aleatoire
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com

# === BASE DE DONNÉES ===
DB_NAME=forex_db
DB_USER=postgres
DB_PASSWORD=motdepasse_securise
DB_HOST=db
DB_PORT=5432

# === REDIS ===
REDIS_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# === RABBITMQ ===
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//

# === CLÉS API FOREX PROVIDERS ===
FIXER_API_KEY=                       # https://fixer.io
OPENEXCHANGERATES_APP_ID=            # https://openexchangerates.org
EXCHANGERATE_API_KEY=                # https://www.exchangerate-api.com
# ECB : pas de clé requise

# === PARAMÈTRES FOREX ENGINE ===
FOREX_CACHE_TTL=300                  # secondes (défaut 5 min)
FOREX_SPREAD_DEFAULT=0.015           # 1.5%
FOREX_MARGIN_DEFAULT=0.005           # 0.5%
FOREX_ANOMALY_THRESHOLD=0.20         # 20% de déviation max

# === CORS (pour l'app mobile) ===
CORS_ALLOWED_ORIGINS=https://votre-app.com,http://localhost:3000
```

---

## 15. État d'avancement

| Composant                          | Statut       | Notes                               |
|------------------------------------|--------------|-------------------------------------|
| Modèles DB complets (8 modèles)    | ✅ Terminé   | Migrations appliquées               |
| 33 devises en base                 | ✅ Terminé   | Données de référence chargées       |
| Agrégateur Forex multi-providers   | ✅ Terminé   | 4 providers, parallèle, anomalies   |
| Rate Engine (tiers, spread, cache) | ✅ Terminé   | Taux croisés, cache Redis           |
| Tous les endpoints API             | ✅ Terminé   | Auth, taux, conversion, historique  |
| Auth JWT + API Keys SHA-256        | ✅ Terminé   | SimpleJWT + hash sécurisé           |
| Rate limiting sliding window       | ✅ Terminé   | Par tier, par IP                    |
| Audit logs                         | ✅ Terminé   | Chaque requête loggée en base       |
| Celery : 5 tâches planifiées       | ✅ Terminé   | Sync, archive, cleanup, health      |
| Docker : 8 services                | ✅ Terminé   | Nginx, Gunicorn, Redis, RabbitMQ…   |
| Swagger UI / OpenAPI               | ✅ Terminé   | drf-spectacular                     |
| Wallets et Transferts              | ✅ Terminé   | Atomique, double-entry ledger       |
| **Clés API providers**             | ⚠️ À faire   | Configurer dans `.env`              |
| Tests unitaires                    | 🔲 À faire   | Priorité prochaine session          |
| CI/CD pipeline                     | 🔲 À faire   | GitHub Actions                      |
| Déploiement cloud                  | 🔲 À faire   | AWS / DigitalOcean / Railway        |
| Monitoring Prometheus + Grafana    | 🔲 À faire   | Phase 2                             |

---

## 16. Roadmap

### Phase 1 — MVP (Actuel ✅)
- API Forex complète (taux, conversion, historique)
- Authentification sécurisée (JWT + API Keys)
- Wallets et transferts basiques
- Infrastructure Docker prête

### Phase 2 — Production
- Tests unitaires et d'intégration (pytest-django)
- SSL/TLS en production (Let's Encrypt)
- CI/CD automatisé (GitHub Actions)
- Monitoring Prometheus + Grafana
- Alertes de taux (push notification quand EUR/USD atteint X)

### Phase 3 — Fonctionnalités avancées
- Support des cryptomonnaies (BTC, ETH, USDT)
- KYC / vérification d'identité
- Intégration paiement (Stripe, virement bancaire)
- Prédiction de taux (Machine Learning)
- Multi-langues (i18n)

---

*ForexPlatform v1.0.0 — World International Business — Mai 2026*
