# NeMo Guardrails SOAR Validation API

A production-ready Flask web API that integrates NVIDIA's NeMo Guardrails framework for input validation in Security Operations Center (SOC) contexts. The API is designed for seamless integration with n8n workflows and automated threat detection systems.

## 🚀 Quick Start

### Docker Hub (Recommended)

```bash
# Pull and run from Docker Hub
docker pull jabarimortadha/nemo-guardrails-soar-api:latest
docker run -p 5000:5000 jabarimortadha/nemo-guardrails-soar-api:latest

# Test the service
curl http://localhost:5000/health
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/MortadhaJabari/NeMo-Guardrails-SimpleTest-API.git
cd NeMo-Guardrails-SimpleTest-API

# Run with Docker Compose
docker-compose up --build

# Test the endpoints
curl -X POST -H "Content-Type: application/json" \
  -d '{"input": "rm -rf /"}' \
  http://localhost:5000/check
```

## 📋 Features

- 🛡️ **Real NeMo Guardrails Integration** - NVIDIA's framework with Colang DSL
- 🔍 **SOAR Pattern Detection** - Specialized for SOC use cases
- 🚫 **Malicious Command Blocking** - Detects dangerous shell commands
- 🌐 **Infrastructure Attack Prevention** - Network reconnaissance detection
- 🔒 **Data Exfiltration Protection** - Identifies data theft attempts
- 🎯 **Persistence Mechanism Detection** - Catches backdoor installations
- 💉 **Command Injection Protection** - Prevents code injection attacks
- 🐳 **Docker Ready** - Production containerization
- 🔗 **n8n Integration** - Workflow automation support
- � **Health Monitoring** - Built-in health checks and logging

## 🔌 API Endpoints

### 1. Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "NeMo Guardrails SOAR Validation API",
  "guardrails_loaded": true
}
```

### 2. Simple Validation (Legacy)
```
POST /check
```

Request:
```json
{
  "input": "rm -rf /"
}
```

Response:
```json
{
  "valid": false,
  "input": "rm -rf /",
  "message": "Content blocked by guardrails"
}
```

### 3. Advanced Validation (Recommended)
```
POST /validate
```

Request:
```json
{
  "text": "nmap -sS target.com",
  "user_id": "soc_analyst_001",
  "session_id": "incident_456"
}
```

Response:
```json
{
  "safe": false,
  "blocked": true,
  "triggered_rail": "infrastructure_attacks",
  "message": "Content blocked by guardrails",
  "details": "Detected network reconnaissance patterns"
}
```
```json
## 🧪 Testing

### Quick Tests

```bash
# Test safe content
curl -X POST -H "Content-Type: application/json" \
  -d '{"input": "What are SOC best practices?"}' \
  http://localhost:5000/check

# Test malicious content
curl -X POST -H "Content-Type: application/json" \
  -d '{"input": "rm -rf /"}' \
  http://localhost:5000/check

# Test with validate endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "nmap -sV 192.168.1.1"}' \
  http://localhost:5000/validate
```

### Comprehensive Test Suite

The project includes a comprehensive Postman test collection in `postman_requests.json` with 60+ test cases covering:

- **Malicious Commands**: File system destruction, disk wiping, system shutdown
- **Infrastructure Attacks**: Network scanning, vulnerability assessment, password cracking
- **Data Exfiltration**: Password file access, data upload/download attempts
- **Persistence Mechanisms**: Cron jobs, service creation, user addition
- **Command Injection**: Command chaining, substitution, pipe injection
- **Safe Content**: Normal queries, documentation requests, friendly conversation
- **Edge Cases**: Empty input, very long strings, encoded commands

## 🐳 Deployment

### Docker Hub (Production Ready)

```bash
# Pull the latest image
docker pull jabarimortadha/nemo-guardrails-soar-api:latest

# Run in production
docker run -d \
  --name nemo-guardrails-api \
  -p 5000:5000 \
  --restart unless-stopped \
  jabarimortadha/nemo-guardrails-soar-api:latest
```

### Docker Compose (Full Stack)

```yaml
version: '3.8'
services:
  nemo-guardrails:
    image: jabarimortadha/nemo-guardrails-soar-api:v1.0.0
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### Advanced Deployment (with Proxy & Monitoring)

For production environments with load balancing and monitoring:

```bash
# Use the included docker-compose.yml with profiles
docker-compose --profile proxy --profile monitoring up -d
```

This includes:
- **nginx reverse proxy** with rate limiting and CORS
- **Redis caching** for improved performance
- **Prometheus metrics** collection
- **Grafana dashboards** for monitoring

## 🔧 Configuration

### Guardrails Configuration

The NeMo Guardrails configuration is located in `guardrails_config/`:

- `config.yml`: Main configuration file specifying input rails
- `rails.co`: Colang patterns for malicious content detection
- `flows.co`: Conversation flow definitions

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port to run the service on (default: 5000)
- `OPENAI_API_KEY`: Optional, for enhanced LLM-based validation

## 🔗 Integration

### n8n Workflow Integration

```json
{
  "method": "POST",
  "url": "http://nemo-guardrails:5000/validate",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "text": "{{ $json.user_input }}",
    "user_id": "{{ $json.user_id }}",
    "session_id": "{{ $json.session_id }}"
  }
}
```

### SOAR Platform Integration

The API can be integrated with SOAR platforms like:
- **Phantom/Splunk SOAR**: Custom actions and playbooks
- **IBM Resilient**: Integration functions
- **Demisto/XSOAR**: Custom scripts and automations

Example integration logic:
```python
# Check if user input is safe before processing
if response['safe']:
    # Proceed with normal workflow
    process_user_input(user_input)
else:
    # Block and alert
    trigger_security_alert(response['triggered_rail'])
```

## 🛡️ Security Patterns Detected

The API detects and blocks:

### Malicious Commands
- File system destruction (`rm -rf /`, `del /s /q C:\`)
- Disk operations (`dd`, `format`)
- System control (`shutdown`, `reboot`)

### Infrastructure Attacks
- Network scanning (`nmap`, `masscan`)
- Vulnerability assessment (`nikto`, `sqlmap`)
- Password attacks (`hydra`, `john`)

### Data Exfiltration
- Sensitive file access (`/etc/passwd`, `/etc/shadow`)
- Data upload attempts (`curl`, `wget`)
- Process information gathering

### Persistence Mechanisms
- Scheduled tasks (`crontab`, `at`)
- Service manipulation (`systemctl`, `service`)
- User account creation (`adduser`, `useradd`)

### Command Injection
- Command chaining (`;`, `&&`, `||`)
- Command substitution (`$()`, backticks)
- Pipe operations (`|`, `>`, `>>`)

## 📊 Monitoring & Health Checks

### Health Endpoint

```bash
curl http://localhost:5000/health
```

Response includes:
- Service status
- Guardrails loading status
- System information

### Docker Health Checks

The container includes built-in health monitoring:
```bash
# Check container health
docker ps
# Should show "healthy" status
```

### Logging

The service provides structured logging for:
- Input validation requests
- Blocked content detection
- System health status
- Performance metrics

## 🔄 Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/MortadhaJabari/NeMo-Guardrails-SimpleTest-API.git
cd NeMo-Guardrails-SimpleTest-API

# Install dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development
python app.py
```

### Building Locally

```bash
# Build the Docker image
docker build -t nemo-guardrails-soar-api .

# Run locally built image
docker run -p 5000:5000 nemo-guardrails-soar-api
```

### Testing Local Changes

```bash
# Run comprehensive tests
# Import postman_requests.json into Postman
# Or use curl commands from the test cases
```

## 📝 Project Structure

```
├── app.py                      # Main Flask application
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Orchestration configuration
├── requirements.txt            # Python dependencies
├── guardrails_config/          # NeMo Guardrails configuration
│   ├── config.yml             # Main config
│   ├── rails.co               # Colang patterns
│   └── flows.co               # Conversation flows
├── postman_requests.json       # Comprehensive test suite
├── nginx.conf                  # Reverse proxy configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Use different port
   docker run -p 8080:5000 jabarimortadha/nemo-guardrails-soar-api:latest
   ```

2. **Container health check failing**
   ```bash
   # Check logs
   docker logs <container-id>
   ```

3. **Memory issues**
   ```bash
   # Increase memory allocation
   docker run -m 2g jabarimortadha/nemo-guardrails-soar-api:latest
   ```

### Performance Tuning

For high-volume environments:
- Use multiple container instances behind a load balancer
- Enable Redis caching
- Tune Gunicorn worker processes
- Monitor resource usage with included Prometheus metrics

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

- **Repository**: [NeMo-Guardrails-SimpleTest-API](https://github.com/MortadhaJabari/NeMo-Guardrails-SimpleTest-API)
- **Docker Hub**: [jabarimortadha/nemo-guardrails-soar-api](https://hub.docker.com/r/jabarimortadha/nemo-guardrails-soar-api)
- **Issues**: GitHub Issues
- **Documentation**: README.md and inline code comments

---

**Version**: 1.0.0  
**Size**: ~1.2GB (includes NeMo Guardrails and dependencies)  
**Platforms**: linux/amd64  
**Technologies**: Python 3.9, NeMo Guardrails 0.8.1, Flask, Docker, Gunicorn
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
