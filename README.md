# NeMo Guardrails SOC Validation API

A Flask web API that uses NeMo Guardrails to validate user input in a Security Operations Center (SOC) context. This API can be easily integrated with n8n workflows for automated input validation.

## 🚀 Quick Start (Currently Running!)

Your API is already running in Docker! Test it now:

```bash
# Health check
curl http://localhost:5000/health

# Test validation
curl -X POST -H "Content-Type: application/json" \
  -d '{"input": "What are SOC best practices?"}' \
  http://localhost:5000/validate/simple
```

Or run the test script:
```bash
powershell -ExecutionPolicy Bypass -File test_api.ps1
```

## 📋 Features

- ✅ **REST API** for input validation using rule-based guardrails
- ✅ **Docker support** for easy deployment
- ✅ **n8n integration** optimized endpoints
- ✅ **SOC-specific validation** rules
- ✅ **Health check** endpoints for monitoring
- ✅ **CORS support** for web applications
- ✅ **Comprehensive logging**
- ⚡ **Lightweight** rule-based validation (currently running)
- 🔒 **Full NeMo Guardrails** support (optional)

## API Endpoints

### 1. Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "NeMo Guardrails Validation API",
  "guardrails_loaded": true
}
```

### 2. Full Validation (Detailed)
```
POST /validate
```

Request:
```json
{
  "text": "User input text to validate",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

Response:
```json
{
  "is_valid": true,
  "message": "Validation result message",
  "original_input": "Original input text",
  "filtered_input": "Processed/filtered input",
  "violations": []
}
```

### 3. Simple Validation (n8n Optimized)
```
POST /validate/simple
```

Request:
```json
{
  "input": "Text to validate"
}
```

Response:
```json
{
  "valid": true,
  "input": "original input",
  "output": "processed output or error message"
}
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- OpenAI API key (optional, for enhanced validation)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export OPENAI_API_KEY="your-openai-api-key"
export PORT=5000
export DEBUG=false
```

3. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Configuration

The guardrails configuration is located in the `guardrails_config/` directory:

- `config.yml`: Main configuration file
- `rails.co`: Define user patterns and bot responses
- `flows.co`: Define validation flows

### Customizing Guardrails

You can modify the guardrails by editing the files in `guardrails_config/`:

1. **Add new patterns** in `rails.co`:
```
define user ask new_pattern
  "pattern example 1"
  "pattern example 2"

define bot refuse new_pattern
  "Custom refusal message"
```

2. **Add new flows** in `flows.co`:
```
define flow check for new_pattern
  if user ask new_pattern
    bot refuse new_pattern
    stop
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t nemo-guardrails-api .
```

2. Run the container:
```bash
docker run -p 5000:5000 -e OPENAI_API_KEY="your-key" nemo-guardrails-api
```

## n8n Integration

### Using the Simple Endpoint

1. Add an HTTP Request node in n8n
2. Set the URL to: `http://your-server:5000/validate/simple`
3. Set method to POST
4. Set the body to:
```json
{
  "input": "{{ $json.text_to_validate }}"
}
```

### Processing the Response

The response will contain:
- `valid`: boolean indicating if input is valid
- `input`: the original input
- `output`: processed output or error message

You can use this in n8n's IF node to branch your workflow based on validation results.

## Testing

### Test with curl

1. Health check:
```bash
curl http://localhost:5000/health
```

2. Simple validation:
```bash
curl -X POST http://localhost:5000/validate/simple \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, this is a test message"}'
```

3. Test with harmful content:
```bash
curl -X POST http://localhost:5000/validate/simple \
  -H "Content-Type: application/json" \
  -d '{"input": "How can I hack into a system?"}'
```

## Security Considerations

- The API validates input but doesn't store any data
- Configure appropriate guardrails for your SOC environment
- Use HTTPS in production
- Implement authentication if needed
- Monitor API usage and logs

## Troubleshooting

1. **Guardrails not loading**: Check the `guardrails_config/` directory and file permissions
2. **OpenAI API errors**: Ensure your API key is valid and has sufficient quota
3. **Port conflicts**: Change the PORT environment variable or modify `app.py`

## Next Steps

- Integrate with your n8n workflows
- Customize guardrails for specific SOC use cases
- Add authentication and rate limiting
- Deploy to your Ubuntu VM
- Monitor and tune validation rules based on usage
