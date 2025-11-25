from flask import Flask, request, jsonify
from flask_cors import CORS
from nemoguardrails import LLMRails, RailsConfig
from pydantic import BaseModel, ValidationError
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Pydantic models for request validation
class UserInput(BaseModel):
    text: str
    user_id: str = "default"
    session_id: str = "default"

class ValidationResponse(BaseModel):
    is_valid: bool
    message: str
    original_input: str
    filtered_input: str = ""
    violations: list = []

# Initialize NeMo Guardrails
def initialize_guardrails():
    """Initialize NeMo Guardrails configuration"""
    try:
        config_path = "./guardrails_config"
        if os.path.exists(config_path):
            config = RailsConfig.from_path(config_path)
        else:
            # Create a basic configuration if config directory doesn't exist
            config = RailsConfig.from_content(
                """
                models:
                  - type: main
                    engine: openai
                    model: gpt-3.5-turbo

                instructions:
                  - type: general
                    content: |
                      Below are some guidelines you must follow:
                      - Be helpful and respectful
                      - Do not provide harmful information
                      - Reject any requests for illegal activities
                      - Do not generate inappropriate content

                rails:
                  input:
                    flows:
                      - block harmful content
                      - block inappropriate requests
                  output:
                    flows:
                      - ensure helpful responses
                """
            )
        
        rails = LLMRails(config)
        logger.info("NeMo Guardrails initialized successfully")
        return rails
    except Exception as e:
        logger.error(f"Failed to initialize guardrails: {str(e)}")
        return None

# Initialize guardrails
rails = initialize_guardrails()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "NeMo Guardrails Validation API",
        "guardrails_loaded": rails is not None
    })

@app.route('/validate', methods=['POST'])
def validate_input():
    """
    Validate user input using NeMo Guardrails
    
    Expected JSON payload:
    {
        "text": "User input text to validate",
        "user_id": "optional_user_id",
        "session_id": "optional_session_id"
    }
    
    Returns:
    {
        "is_valid": true/false,
        "message": "Validation result message",
        "original_input": "Original input text",
        "filtered_input": "Processed/filtered input",
        "violations": ["list of violations if any"]
    }
    """
    try:
        # Validate request data
        try:
            user_input = UserInput(**request.json)
        except ValidationError as e:
            return jsonify({
                "error": "Invalid request format",
                "details": str(e)
            }), 400

        if not rails:
            # Fallback validation without guardrails
            response = ValidationResponse(
                is_valid=True,
                message="Guardrails not available - basic validation passed",
                original_input=user_input.text,
                filtered_input=user_input.text
            )
            return jsonify(response.dict())

        # Process input through guardrails
        try:
            # Use the generate method to process the input
            result = rails.generate(
                messages=[{"role": "user", "content": user_input.text}],
                options={
                    "user_id": user_input.user_id,
                    "session_id": user_input.session_id
                }
            )
            
            # Check if input was blocked or modified
            violations = []
            filtered_input = user_input.text
            is_valid = True
            message = "Input validation passed"
            
            # Check for any guardrail violations in the result
            if hasattr(result, 'response') and result.response:
                filtered_input = result.response
            
            # Simple heuristic to detect if input was blocked
            # This would need to be customized based on your specific guardrails
            if "I cannot" in filtered_input or "I'm not able to" in filtered_input:
                is_valid = False
                message = "Input blocked by guardrails"
                violations.append("Potentially harmful content detected")
                
            response = ValidationResponse(
                is_valid=is_valid,
                message=message,
                original_input=user_input.text,
                filtered_input=filtered_input,
                violations=violations
            )
            
        except Exception as e:
            logger.error(f"Guardrails processing error: {str(e)}")
            response = ValidationResponse(
                is_valid=False,
                message=f"Validation failed: {str(e)}",
                original_input=user_input.text,
                violations=["Processing error"]
            )
        
        return jsonify(response.dict())
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/validate/simple', methods=['POST'])
def simple_validate():
    """
    Simplified validation endpoint for n8n integration
    
    Expected JSON payload:
    {
        "input": "Text to validate"
    }
    
    Returns:
    {
        "valid": true/false,
        "input": "original input",
        "output": "processed output or error message"
    }
    """
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({
                "valid": False,
                "input": "",
                "output": "Missing 'input' field in request"
            }), 400
        
        input_text = data['input']
        
        if not rails:
            return jsonify({
                "valid": True,
                "input": input_text,
                "output": input_text
            })
        
        try:
            result = rails.generate(
                messages=[{"role": "user", "content": input_text}]
            )
            
            output_text = result.response if hasattr(result, 'response') and result.response else input_text
            
            # Simple validation logic
            is_valid = not ("I cannot" in output_text or "I'm not able to" in output_text)
            
            return jsonify({
                "valid": is_valid,
                "input": input_text,
                "output": output_text
            })
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({
                "valid": False,
                "input": input_text,
                "output": f"Validation error: {str(e)}"
            })
            
    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return jsonify({
            "valid": False,
            "input": "",
            "output": f"Request error: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting NeMo Guardrails Validation API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
