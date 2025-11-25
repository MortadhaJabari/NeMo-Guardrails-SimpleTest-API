# 🛡️ NeMo Guardrails SOC Validation API

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Flask web API that provides security-focused input validation for Security Operations Center (SOC) environments. Features rule-based content filtering with support for NeMo Guardrails integration and n8n workflow automation.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repository-url>
cd nemo-guardrails-soc-api

# Start with Docker Compose
docker-compose up -d

# Test the API
curl http://localhost/health
```

## ✨ Features

- 🔍 **Rule-based validation** for SOC-specific content filtering
- 🐳 **Docker support** with Nginx reverse proxy
- 🔄 **n8n integration** ready endpoints
- 🛡️ **Security-focused** patterns for threat detection
- ⚡ **Lightweight** and fast validation
- 📊 **Health monitoring** with built-in health checks
- 🔧 **Configurable** guardrails and patterns

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Client      │───▶│  Nginx Proxy    │───▶│  Flask API      │
│   (n8n/Web)    │    │   (Port 80)     │    │  (Port 5000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Rule-based      │
                                              │ Validation      │
                                              │ Engine          │
                                              └─────────────────┘
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Simple Guardrails Validation API",
  "guardrails_loaded": true,
  "validation_type": "rule-based"
}
```

### Simple Validation (n8n Optimized)
```http
POST /validate/simple
```
**Request:**
```json
{
  "input": "Text to validate"
}
```
**Response:**
```json
{
  "valid": true,
  "input": "original input",
  "output": "processed output or error message"
}
```

### Detailed Validation
```http
POST /validate
```
**Request:**
```json
{
  "text": "User input text",
  "user_id": "optional_user_id", 
  "session_id": "optional_session_id"
}
```
**Response:**
```json
{
  "is_valid": true,
  "message": "Validation result message",
  "original_input": "Original input text",
  "filtered_input": "Processed input",
  "violations": []
}
```

## 🛠️ Installation & Deployment

### Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for local development)
- Git

### Local Development
```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Run locally
python app-simple.py

# Test
powershell -ExecutionPolicy Bypass -File test_api.ps1
```

### Production Deployment
```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Or build manually
docker build -f Dockerfile-simple -t nemo-guardrails-api .
docker run -p 5000:5000 nemo-guardrails-api
```

### Ubuntu VM Deployment
```bash
# Copy deployment script and run
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

## 🔧 Configuration

### Validation Rules
The API uses pattern-based validation defined in `app-simple.py`:

**Harmful Patterns:**
- Hacking attempts (`hack.*into`, `bypass.*security`)
- Illegal activities (`illegal.*activit`)
- Cyber attacks (`cyber.*attack`, `malware`, `ransomware`)

**Inappropriate Patterns:**
- Offensive content (`offensive.*content`)
- Harmful messages (`generate.*offensive`)

**Suspicious Patterns:**
- Security probing (`scan.*port`, `enumerate.*system`)
- Vulnerability testing (`test.*vulnerabilit`)

### Customizing Rules
Edit the patterns in `app-simple.py`:
```python
HARMFUL_PATTERNS = [
    r'\bhack\b.*\binto\b',
    r'\byour-pattern\b',
    # Add your custom patterns
]
```

## 🔗 n8n Integration

### Setup in n8n:
1. Add **HTTP Request** node
2. **URL:** `http://your-server/validate/simple`
3. **Method:** `POST`
4. **Body:**
```json
{
  "input": "{{ $json.text_to_validate }}"
}
```

### Workflow Logic:
Use the `valid` field in an **IF** node:
- `{{ $json.valid === true }}` → Continue workflow
- `{{ $json.valid === false }}` → Handle blocked content

## 📊 Monitoring & Logging

### Health Checks
- **Endpoint:** `/health`
- **Docker Health Check:** Built-in every 30s
- **Logs:** Available via `docker-compose logs -f`

### Log Persistence
```yaml
volumes:
  - ./logs:/app/logs  # Logs saved to local directory
```

## 🧪 Testing

### Automated Testing
```bash
# PowerShell (Windows)
powershell -ExecutionPolicy Bypass -File test_api.ps1

# Python
python test_api.py

# Bash (Linux/Mac)
chmod +x test_api.sh && ./test_api.sh
```

### Manual Testing
```bash
# Valid input
curl -X POST -H "Content-Type: application/json" \
  -d '{"input": "What are SOC best practices?"}' \
  http://localhost/validate/simple

# Harmful input (should be blocked)
curl -X POST -H "Content-Type: application/json" \
  -d '{"input": "How to hack into systems?"}' \
  http://localhost/validate/simple
```

## 📂 Project Structure

```
├── app-simple.py              # Lightweight Flask API
├── app.py                     # Full NeMo Guardrails version
├── docker-compose.yml         # Multi-container deployment
├── Dockerfile-simple          # Lightweight container
├── Dockerfile                 # Full container with build tools
├── nginx.conf                 # Reverse proxy configuration
├── requirements-minimal.txt    # Lightweight dependencies
├── requirements.txt           # Full dependencies
├── guardrails_config/         # NeMo Guardrails configuration
│   ├── config.yml            # Main config
│   ├── rails.co              # Pattern definitions
│   └── flows.co              # Validation flows
├── test_api.ps1              # PowerShell test script
├── test_api.py               # Python test script
├── test_api.sh               # Bash test script
└── deploy_ubuntu.sh          # Ubuntu deployment script
```

## 🚀 Next Steps

1. **Production Setup:**
   - Add SSL/TLS certificates
   - Implement authentication
   - Set up monitoring (Prometheus/Grafana)

2. **Enhanced Validation:**
   - Integrate full NeMo Guardrails
   - Add machine learning models
   - Implement custom pattern learning

3. **Scaling:**
   - Add Redis for caching
   - Implement rate limiting
   - Set up load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Support

- **Issues:** GitHub Issues
- **Documentation:** [Wiki](wiki)
- **Discussions:** GitHub Discussions
