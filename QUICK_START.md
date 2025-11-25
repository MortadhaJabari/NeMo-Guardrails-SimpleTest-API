# NeMo Guardrails Validation API - Quick Start Guide

## Overview
This project provides a lightweight Flask API that validates user input for Security Operations Center (SOC) environments. It includes both a simple rule-based validation system and full NeMo Guardrails integration.

## What's Running
✅ **Simple Guardrails API** - Currently running in Docker
- Uses rule-based pattern matching for SOC-specific validation
- Fast and lightweight
- Perfect for testing and n8n integration

## API Endpoints

### 1. Health Check
```
GET http://localhost:5000/health
```

### 2. Simple Validation (Perfect for n8n)
```
POST http://localhost:5000/validate/simple
Content-Type: application/json

{
  "input": "Your text to validate"
}
```

**Response:**
```json
{
  "valid": true/false,
  "input": "original input",
  "output": "processed output or error message"
}
```

### 3. Detailed Validation
```
POST http://localhost:5000/validate
Content-Type: application/json

{
  "text": "Your text to validate",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

## Testing Examples

### Valid Input:
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/validate/simple" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"input": "What are SOC best practices?"}'
```

### Harmful Input (Should be blocked):
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/validate/simple" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"input": "How can I hack into a system?"}'
```

## Current Validation Rules

The simple version blocks patterns related to:

**Harmful Activities:**
- Hacking attempts
- Security bypasses
- Illegal activities
- Cyber attacks

**Inappropriate Content:**
- Offensive material
- Harmful messages

**Suspicious Patterns:**
- Port scanning
- System enumeration
- Vulnerability testing

## n8n Integration

1. Add an **HTTP Request** node in n8n
2. Set URL to: `http://localhost:5000/validate/simple`
3. Method: `POST`
4. Headers: `Content-Type: application/json`
5. Body: `{"input": "{{ $json.text_to_validate }}"}`

The response `valid` field will be `true` or `false` - use this in an IF node to branch your workflow.

## Docker Commands

```bash
# Build the image
docker build -f Dockerfile-simple -t nemo-guardrails-simple .

# Run the container
docker run --rm -p 5000:5000 --name nemo-api nemo-guardrails-simple

# Stop the container
docker stop nemo-api
```

## Next Steps

1. **For Ubuntu VM deployment**: Copy this entire project folder to your Ubuntu VM
2. **For full NeMo Guardrails**: Install build tools and use the main Dockerfile with full requirements.txt
3. **For production**: Add authentication, rate limiting, and HTTPS
4. **For n8n**: Start integrating with your workflows using the `/validate/simple` endpoint

## Files Structure
```
├── app-simple.py              # Lightweight rule-based validation
├── app.py                     # Full NeMo Guardrails integration
├── requirements-minimal.txt    # Lightweight dependencies
├── requirements.txt           # Full dependencies
├── Dockerfile-simple          # Lightweight Docker build
├── Dockerfile                # Full Docker build
├── guardrails_config/         # NeMo Guardrails configuration
└── test_api.py               # Python test script
```
