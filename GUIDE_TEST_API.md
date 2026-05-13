# 📋 GUIDE DE TEST — ForexPlatform API
**Version** : 1.0  
**Date** : 13 Mai 2026  
**Destinataire** : Équipe Technique / Chef de Projet  
**Statut** : Prêt pour test d'intégration mobile  

---

## 📌 RÉSUMÉ EXÉCUTIF

L'API **ForexPlatform** est opérationnelle et prête à être intégrée dans l'application mobile.  
Elle permet de :
- Récupérer les taux de change en **temps réel** (source : Banque Centrale Européenne)
- Convertir des montants entre **33 devises** internationales
- Gérer des **wallets multi-devises** par utilisateur
- Effectuer des **transferts** entre utilisateurs

---

## 🔧 INFORMATIONS DE CONNEXION

| Paramètre | Valeur |
|-----------|--------|
| **URL de base** | `http://127.0.0.1:8000` |
| **Version API** | `v1` |
| **Format** | JSON |
| **Authentification** | Clé API (header `X-API-KEY`) |

---

## 🔑 CLÉ API POUR LES TESTS

```
X-API-KEY: fxp_oNGqt67mlKz40hl0Me748a1rQQwMD0qrjVB1pL16xOY
```

> ⚠️ Cette clé est réservée aux tests. Une clé de production sera générée avant le déploiement.

---

## 📥 INSTALLATION DE POSTMAN

1. Télécharger Postman : https://www.postman.com/downloads/
2. Installer et ouvrir Postman
3. Importer la collection fournie :
   - Cliquer **Import** → sélectionner le fichier `ForexPlatform.postman_collection.json`

---

## 🚀 TESTS À EFFECTUER

---

### ✅ TEST 1 — Vérification de l'API (Health Check)

**Objectif** : Confirmer que le serveur fonctionne.

| | |
|-|-|
| **Méthode** | `GET` |
| **URL** | `http://127.0.0.1:8000/api/v1/health/` |
| **Auth** | Aucune |
| **Body** | Aucun |

**Dans Postman** :
1. Méthode : `GET`
2. URL : `http://127.0.0.1:8000/api/v1/health/`
3. Cliquer **Send**

**Réponse attendue (200 OK)** :
```json
{
  "status": "ok",
  "service": "ForexPlatform API",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

---

### ✅ TEST 2 — Liste des devises disponibles

**Objectif** : Récupérer les 33 devises supportées.

| | |
|-|-|
| **Méthode** | `GET` |
| **URL** | `http://127.0.0.1:8000/api/v1/currencies/` |
| **Auth** | Aucune |
| **Body** | Aucun |

**Réponse attendue (200 OK)** :
```json
{
  "success": true,
  "count": 33,
  "currencies": [
    {"code": "EUR", "name": "Euro", "symbol": "€"},
    {"code": "USD", "name": "US Dollar", "symbol": "$"},
    {"code": "GBP", "name": "British Pound", "symbol": "£"},
    ...
  ]
}
```

---

### ✅ TEST 3 — Récupérer un taux de change en temps réel

**Objectif** : Obtenir le taux EUR/USD en direct depuis la Banque Centrale Européenne.

| | |
|-|-|
| **Méthode** | `GET` |
| **URL** | `http://127.0.0.1:8000/api/v1/rates/EUR/USD/` |
| **Auth** | Clé API (voir ci-dessous) |
| **Body** | Aucun |

**Configuration dans Postman** :

Onglet **Headers** :
| Key | Value |
|-----|-------|
| `X-API-KEY` | `fxp_oNGqt67mlKz40hl0Me748a1rQQwMD0qrjVB1pL16xOY` |

**Réponse attendue (200 OK)** :
```json
{
  "success": true,
  "source": "live",
  "rate": {
    "pair": "EUR/USD",
    "from_currency": "EUR",
    "to_currency": "USD",
    "market_rate": "1.17",
    "timestamp": "2026-05-13T16:44:57Z"
  }
}
```

**Autres paires à tester** :
```
GET /api/v1/rates/USD/GBP/
GET /api/v1/rates/EUR/JPY/
GET /api/v1/rates/USD/CAD/
GET /api/v1/rates/GBP/EUR/
```

---

### ✅ TEST 4 — Conversion de montant (fonctionnalité principale)

**Objectif** : Convertir un montant d'une devise vers une autre.

| | |
|-|-|
| **Méthode** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/v1/convert/` |
| **Auth** | Clé API |
| **Body** | JSON (voir ci-dessous) |

**Configuration dans Postman** :

Onglet **Headers** :
| Key | Value |
|-----|-------|
| `X-API-KEY` | `fxp_oNGqt67mlKz40hl0Me748a1rQQwMD0qrjVB1pL16xOY` |
| `Content-Type` | `application/json` |

Onglet **Body** → **raw** → **JSON** :
```json
{
  "from_currency": "EUR",
  "to_currency": "USD",
  "amount": 500
}
```

**Réponse attendue (200 OK)** :
```json
{
  "success": true,
  "conversion": {
    "from_currency": "EUR",
    "to_currency": "USD",
    "amount": "500",
    "converted_amount": "595.5300",
    "market_rate": "1.17",
    "business_rate": "1.19106000",
    "spread_pct": "1.50",
    "fee_amount": "8.9330",
    "tier": "standard",
    "source": "live",
    "timestamp": "2026-05-13T16:47:01Z"
  }
}
```

**Explication des champs** :
| Champ | Signification |
|-------|---------------|
| `converted_amount` | Montant final reçu par le bénéficiaire |
| `market_rate` | Taux brut du marché (BCE) |
| `business_rate` | Taux appliqué (marché + marge) |
| `spread_pct` | Commission en % (1.5% pour tier standard) |
| `fee_amount` | Montant des frais en devise source |

**Autres conversions à tester** :
```json
{"from_currency": "USD", "to_currency": "GBP", "amount": 1000}
{"from_currency": "EUR", "to_currency": "JPY", "amount": 250}
{"from_currency": "GBP", "to_currency": "EUR", "amount": 750}
```

---

### ✅ TEST 5 — Cas d'erreurs (validation)

**Objectif** : Vérifier que l'API rejette correctement les données invalides.

#### 5a. Montant négatif → doit retourner 400
```json
{
  "from_currency": "EUR",
  "to_currency": "USD",
  "amount": -50
}
```
**Réponse attendue** :
```json
{"success": false, "error": "amount must be a positive number."}
```

#### 5b. Devise inconnue → doit retourner 404
```
GET http://127.0.0.1:8000/api/v1/rates/EUR/XYZ/
```
**Réponse attendue** :
```json
{"success": false, "error": "Rate EUR/XYZ not available."}
```

#### 5c. Clé API invalide → doit retourner 403
```
X-API-KEY: fxp_INVALIDE
```
**Réponse attendue** :
```json
{"detail": "Clé API invalide ou expirée."}
```

#### 5d. Champ manquant → doit retourner 400
```json
{
  "from_currency": "EUR",
  "amount": 100
}
```
**Réponse attendue** :
```json
{"success": false, "error": "from_currency, to_currency and amount are required."}
```

---

### ✅ TEST 6 — Authentification JWT (pour les fonctions utilisateur)

**Objectif** : Se connecter et accéder aux fonctionnalités avancées (wallets, transferts).

| | |
|-|-|
| **Méthode** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/v1/auth/token/` |
| **Auth** | Aucune |
| **Body** | JSON |

```json
{
  "username": "WIB",
  "password": "homeboY2026"
}
```

**Réponse attendue (200 OK)** :
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci..."
}
```

> Copier la valeur de `"access"` et l'utiliser dans les tests suivants comme :
> `Authorization: Bearer eyJhbGci...`

---

### ✅ TEST 7 — Wallets

**Objectif** : Créer et consulter un wallet.

#### 7a. Créer un wallet EUR
| | |
|-|-|
| **Méthode** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/v1/wallets/` |
| **Auth** | `Authorization: Bearer {token}` |

```json
{"currency_code": "EUR"}
```

**Réponse (201 Created)** :
```json
{
  "success": true,
  "created": true,
  "wallet": {
    "id": "65d299fd-e1bb-4422-...",
    "currency": "EUR",
    "balance": "0",
    "is_active": true
  }
}
```

#### 7b. Liste de mes wallets
```
GET http://127.0.0.1:8000/api/v1/wallets/
Authorization: Bearer {token}
```

---

## 📱 INTÉGRATION DANS L'APP MOBILE

### Méthode recommandée : Clé API dans le header

L'app mobile n'a **pas besoin de login** pour les taux et conversions.  
Il suffit d'ajouter **un seul header** à chaque requête :

```
X-API-KEY: fxp_oNGqt67mlKz40hl0Me748a1rQQwMD0qrjVB1pL16xOY
```

### Exemple Flutter (Dart)
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

const String API_KEY = 'fxp_oNGqt67mlKz40hl0Me748a1rQQwMD0qrjVB1pL16xOY';
const String BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Récupérer le taux EUR/USD
Future<double> getRate(String from, String to) async {
  final response = await http.get(
    Uri.parse('$BASE_URL/rates/$from/$to/'),
    headers: {'X-API-KEY': API_KEY},
  );
  final data = jsonDecode(response.body);
  return double.parse(data['rate']['market_rate']);
}

// Convertir un montant
Future<Map> convert(String from, String to, double amount) async {
  final response = await http.post(
    Uri.parse('$BASE_URL/convert/'),
    headers: {
      'X-API-KEY': API_KEY,
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'from_currency': from,
      'to_currency': to,
      'amount': amount,
    }),
  );
  return jsonDecode(response.body)['conversion'];
}
```

### Exemple React Native (JavaScript)
```javascript
const API_KEY = 'fxp_oNGqt67mlKz40hl0Me748a1rQQwMD0qrjVB1pL16xOY';
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Récupérer le taux
const getRate = async (from, to) => {
  const res = await fetch(`${BASE_URL}/rates/${from}/${to}/`, {
    headers: { 'X-API-KEY': API_KEY }
  });
  const data = await res.json();
  return data.rate.market_rate;
};

// Convertir
const convert = async (from, to, amount) => {
  const res = await fetch(`${BASE_URL}/convert/`, {
    method: 'POST',
    headers: {
      'X-API-KEY': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ from_currency: from, to_currency: to, amount })
  });
  const data = await res.json();
  return data.conversion;
};
```

---

## 📊 TABLEAU DES CODES DE RÉPONSE

| Code | Signification | Action recommandée |
|------|---------------|-------------------|
| `200` | Succès | Afficher le résultat |
| `201` | Créé avec succès | Confirmer à l'utilisateur |
| `400` | Données invalides | Afficher le message d'erreur |
| `401` | Non authentifié | Redemander le login |
| `403` | Clé API invalide | Vérifier la clé API |
| `404` | Devise non trouvée | Informer l'utilisateur |
| `429` | Trop de requêtes | Attendre 1 heure |
| `503` | Service temporairement indisponible | Réessayer dans quelques secondes |

---

## 🌍 DEVISES SUPPORTÉES (33 au total)

| Code | Devise | Région |
|------|--------|--------|
| USD | Dollar américain | Amériques |
| EUR | Euro | Europe |
| GBP | Livre sterling | Europe |
| JPY | Yen japonais | Asie |
| CHF | Franc suisse | Europe |
| CAD | Dollar canadien | Amériques |
| AUD | Dollar australien | Océanie |
| CNY | Yuan chinois | Asie |
| INR | Roupie indienne | Asie |
| BRL | Real brésilien | Amériques |
| ZAR | Rand sud-africain | Afrique |
| NGN | Naira nigérian | Afrique |
| EGP | Livre égyptienne | Afrique |
| AED | Dirham émirati | Moyen-Orient |
| SAR | Riyal saoudien | Moyen-Orient |
| TRY | Livre turque | Europe/Asie |
| MXN | Peso mexicain | Amériques |
| KRW | Won sud-coréen | Asie |
| SGD | Dollar singapourien | Asie |
| HKD | Dollar de Hong Kong | Asie |
| SEK | Couronne suédoise | Europe |
| NOK | Couronne norvégienne | Europe |
| DKK | Couronne danoise | Europe |
| NZD | Dollar néo-zélandais | Océanie |
| THB | Baht thaïlandais | Asie |
| MYR | Ringgit malaisien | Asie |
| IDR | Roupie indonésienne | Asie |
| PHP | Peso philippin | Asie |
| VND | Dong vietnamien | Asie |
| PLN | Zloty polonais | Europe |
| RUB | Rouble russe | Europe/Asie |
| COP | Peso colombien | Amériques |
| CLP | Peso chilien | Amériques |

---

## ⚡ LIMITES PAR TIER

| Tier | Requêtes/heure | Usage |
|------|----------------|-------|
| **Free** | 100 | Tests et développement |
| **Standard** | 1 000 | App mobile production |
| **Premium** | 5 000 | Usage intensif |
| **Partner** | 50 000 | Intégration entreprise |

La clé de test fournie est en tier **Standard** (1 000 requêtes/heure).

---

## ✅ CHECKLIST AVANT INTÉGRATION APK

Avant de builder le nouvel APK, confirmer que :

- [ ] Test 1 — Health Check retourne `200 ok`
- [ ] Test 2 — La liste des 33 devises s'affiche correctement
- [ ] Test 3 — Le taux EUR/USD est récupéré en temps réel
- [ ] Test 4 — La conversion fonctionne avec différentes devises
- [ ] Test 5a — Un montant négatif retourne bien une erreur `400`
- [ ] Test 5b — Une devise inconnue retourne bien une erreur `404`
- [ ] Test 5c — Une clé invalide retourne bien une erreur `403`
- [ ] Test 6 — Le login JWT fonctionne
- [ ] Test 7 — La création de wallet fonctionne
- [ ] L'équipe mobile a bien intégré le header `X-API-KEY` dans les requêtes
- [ ] L'URL de base est correcte (`http://127.0.0.1:8000` en dev, à remplacer par l'URL de prod)

---

## 📞 CONTACTS

| Rôle | Responsabilité |
|------|----------------|
| **Développeur Backend** | API, endpoints, corrections de bugs |
| **Équipe Mobile** | Intégration dans Flutter/React Native, build APK |

---

*Document généré le 13 Mai 2026 — ForexPlatform API v1.0*
