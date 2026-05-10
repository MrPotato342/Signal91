# Signal91 — India Phone Intelligence API

Signal91 is a developer-focused India phone intelligence API for telecom metadata lookup and mobile number enrichment.

The API analyzes Indian mobile numbers and returns structured telecom intelligence signals such as:

* carrier detection
* telecom circle
* line type
* validation metadata

Designed for:

* fraud prevention
* onboarding verification
* CRM enrichment
* lead validation
* telecom analytics
* identity workflows

---

# Authentication

Authentication is handled through RapidAPI.

All requests must include:

* `X-RapidAPI-Key`
* `X-RapidAPI-Host`

These headers are automatically generated in the RapidAPI dashboard and code snippets.

---

# Base URL

```text
https://YOUR_API_NAME.p.rapidapi.com
```

---

# Endpoints

---

## POST `/analyze`

Analyze a single Indian phone number.

### Request Body

```json
{
  "phone": "9876543210"
}
```

### Example Request

```bash
curl --request POST \
  --url https://YOUR_API_NAME.p.rapidapi.com/analyze \
  --header 'Content-Type: application/json' \
  --header 'X-RapidAPI-Key: YOUR_API_KEY' \
  --header 'X-RapidAPI-Host: YOUR_API_NAME.p.rapidapi.com' \
  --data '{
    "phone": "9876543210"
}'
```

### Example Response

```json
input: 7624931344
normalization: {'raw_input': '7624931344', 'digits': '7624931344', 'normalized': '+917624931344', 'country_code': '91', 'inferred_country': 'IN', 'parse_confidence': 0.95, 'parse_strategy': 'indian_local_mobile'}
classification: {'is_valid': True, 'type': 'indian_mobile'}
summary: {'valid': True, 'type': 'indian_mobile', 'carrier': 'AT', 'circle': 'KA', 'risk_score': 0, 'risk_level': 'low', 'reachability_probability': 0.94, 'reachability_level': 'high', 'whatsapp_probability': 1.0, 'whatsapp_likelihood': 'very_likely', 'overall_confidence': 0.83}
success: True
telecom: {'carrier': 'AT', 'circle': 'KA', 'matched_prefix': '7624', 'prefix_match_length': 4}
risk: {'risk_score': 0, 'risk_flags': []}
reachability: {'reachability_probability': 0.94, 'reachability_confidence': 0.74, 'reachability_level': 'high', 'reachability_reasons': ['known_carrier', 'known_circle', '4digit_msc_match']}
whatsapp: {'whatsapp_probability': 1.0, 'whatsapp_confidence': 0.8, 'whatsapp_likelihood': 'very_likely', 'whatsapp_reasons': ['high_reachability', 'known_carrier', 'known_circle']}
features: {'length': 10, 'starts_valid': True, 'has_valid_5digit_msc': False, 'has_valid_4digit_msc': True, 'carrier_known': True, 'circle_known': True, 'unique_digits': 7, 'most_common_digit_count': 3, 'repeated_digit_ratio': 0.3, 'digit_entropy': 2.6464, 'is_sequential_ascending': False, 'is_sequential_descending': False, 'has_repeating_2digit_pattern': False, 'has_repeating_3digit_pattern': False, 'is_mirrored': False, 'max_consecutive_run': 2, 'starts_with_99999': False, 'starts_with_12345': False, 'starts_with_00000': False, 'human_probability_score': 100}
intelligence_confidence: 0.83
```

---

## GET `/health`

Health check endpoint.

### Example Response

```json
{
  "success": true,
  "status": "ok"
}
```

---

# Error Responses

## 400 — Invalid Request

```json
{
  "success": false,
  "error": "Invalid request"
}
```

---

## 401 — Unauthorized

```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

## 429 — Rate Limit Exceeded

```json
{
  "success": false,
  "error": "Rate limit exceeded"
}
```

---

## 500 — Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

# Input Rules

Phone number requirements:

* Indian phone numbers only (International numbers have limited intelligence)
* Any input format is accepted, garbage is automatically filtered.  eg: ("call me +91xxxxxxxxxx" is the same as "91xxxxxxxxxx")

Examples:

* `9876543210`
* `+919876543210`

---

# Usage Notes

Signal91 is intended for lawful verification and enrichment workflows only.

Do not use this API for:

* unsolicited marketing
* scraping
* surveillance
* unauthorized profiling
* abusive automation

---

# Performance

* Low-latency API responses
* JSON-based REST interface
* Optimized for backend integrations and automation workflows

---

# Support

For support, feature requests, or enterprise access, contact the API provider through RapidAPI.
