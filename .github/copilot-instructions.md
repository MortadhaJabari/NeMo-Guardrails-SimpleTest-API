<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Project Context
This is a Flask web API project that integrates NeMo Guardrails for input validation in a Security Operations Center (SOC) context. The API is designed to be integrated with n8n workflows for automated content validation.

## Key Components
- Flask web server with REST API endpoints
- NeMo Guardrails integration for content validation
- SOC-specific guardrails configuration
- Docker support for deployment
- n8n integration endpoints

## Coding Standards
- Use Python type hints where possible
- Follow PEP 8 style guidelines
- Include comprehensive error handling
- Add logging for debugging and monitoring
- Use Pydantic models for request/response validation

## Security Considerations
- This is a security-focused application for SOC environments
- Input validation should be thorough and comprehensive
- Error messages should not leak sensitive information
- Follow security best practices for API development

## Integration Requirements
- API endpoints should be n8n-friendly (simple JSON input/output)
- Responses should be consistent and predictable
- Include health check endpoints for monitoring
