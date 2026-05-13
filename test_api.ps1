$BASE = "http://127.0.0.1:8000/api/v1"

function Test-Endpoint {
    param($label, $uri, $method="GET", $body=$null, $headers=@{})
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host " $label" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Blue
    try {
        $params = @{Uri=$uri; Method=$method; UseBasicParsing=$true; Headers=$headers; ErrorAction="Stop"}
        if ($body) { $params.Body = $body; $params.ContentType = "application/json" }
        $r = Invoke-WebRequest @params
        Write-Host "STATUS: $($r.StatusCode) OK" -ForegroundColor Green
        $r.Content | ConvertFrom-Json | ConvertTo-Json -Depth 4
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        Write-Host "STATUS: $code ERREUR" -ForegroundColor Red
        try { $_.Exception.Response.GetResponseStream() | ForEach-Object { $reader = New-Object System.IO.StreamReader($_); $reader.ReadToEnd() } } catch {}
    }
}

# === 1. Health (sans auth) ===
Test-Endpoint "1. Health Check" "$BASE/health/"

# === 2. Login -> recuperer JWT ===
Write-Host "`n========================================" -ForegroundColor Blue
Write-Host " 2. Authentification JWT" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Blue
$resp = Invoke-WebRequest -Uri "$BASE/auth/token/" -Method POST -ContentType "application/json" -Body '{"username":"WIB","password":"homeboY2026"}' -UseBasicParsing
$token = ($resp.Content | ConvertFrom-Json).access
Write-Host "STATUS: 200 OK" -ForegroundColor Green
Write-Host "Access token: $($token.Substring(0,40))..."
$H = @{Authorization="Bearer $token"}

# === 3. Currencies ===
Test-Endpoint "3. Liste des 33 devises" "$BASE/currencies/"

# === 4. Taux EUR/USD temps reel ===
Test-Endpoint "4. Taux EUR/USD (temps reel)" "$BASE/rates/EUR/USD/" "GET" $null $H

# === 5. Taux USD/JPY ===
Test-Endpoint "5. Taux USD/JPY (temps reel)" "$BASE/rates/USD/JPY/" "GET" $null $H

# === 6. Conversion 500 EUR -> USD ===
Test-Endpoint "6. Conversion 500 EUR -> USD" "$BASE/convert/" "POST" '{"from_currency":"EUR","to_currency":"USD","amount":500}' $H

# === 7. Conversion 1000 USD -> GBP ===
Test-Endpoint "7. Conversion 1000 USD -> GBP" "$BASE/convert/" "POST" '{"from_currency":"USD","to_currency":"GBP","amount":1000}' $H

# === 8. Conversion invalide (montant negatif) ===
Test-Endpoint "8. Montant invalide (-50)" "$BASE/convert/" "POST" '{"from_currency":"EUR","to_currency":"USD","amount":-50}' $H

# === 9. Devise inconnue ===
Test-Endpoint "9. Devise inconnue (EUR->XYZ)" "$BASE/rates/EUR/XYZ/" "GET" $null $H

# === 10. Creer wallet EUR ===
Test-Endpoint "10. Creer wallet EUR" "$BASE/wallets/" "POST" '{"currency_code":"EUR"}' $H

# === 11. Creer wallet USD ===
Test-Endpoint "11. Creer wallet USD" "$BASE/wallets/" "POST" '{"currency_code":"USD"}' $H

# === 12. Liste wallets ===
Test-Endpoint "12. Liste wallets" "$BASE/wallets/" "GET" $null $H

# === 13. Creer une API Key ===
Test-Endpoint "13. Creer API Key (tier standard)" "$BASE/api-keys/create/" "POST" '{"name":"MonApp","tier":"standard"}' $H

# === 14. Liste API Keys ===
Test-Endpoint "14. Liste API Keys" "$BASE/api-keys/" "GET" $null $H

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " TESTS TERMINES" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
