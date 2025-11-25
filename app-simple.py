from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
import os
import logging
import re
from typing import Dict, Any, List

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
    violations: List[str] = []

# Simple rule-based validation patterns for SOC context
HARMFUL_PATTERNS = [
    r'\bhack\b.*\binto\b',
    r'\bbypass\b.*\bsecurity\b',
    r'\bbreak\b.*\binto\b',
    r'\billegal\b.*\bactivit',
    r'\bcyber\b.*\battack',
    r'\bexploit\b.*\bvulnerabilit',
    r'\bmalware\b',
    r'\bransomware\b',
    r'\bphishing\b.*\bscam\b',
]

INAPPROPRIATE_PATTERNS = [
    r'\boffensive\b.*\bcontent\b',
    r'\binappropriate\b.*\bmaterial\b',
    r'\bharming\b.*\bmessage\b',
    r'\bgenerate\b.*\boffensive\b',
]

SUSPICIOUS_PATTERNS = [
    r'\bscan\b.*\bport\b',
    r'\benumerate\b.*\bsystem\b',
    r'\bprobe\b.*\bweakness\b',
    r'\btest\b.*\bvulnerabilit\b',
    r'\bsql\b.*\binjection\b',
]

def simple_guardrails_check(text: str) -> tuple[bool, str, List[str]]:
    """
    Simple rule-based validation for SOC context
    Returns: (is_valid, filtered_text, violations)
    """
    text_lower = text.lower()
    violations = []
    
    # Check for harmful patterns
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            violations.append(f"Harmful content detected: {pattern}")
    
    # Check for inappropriate patterns
    for pattern in INAPPROPRIATE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            violations.append(f"Inappropriate content detected: {pattern}")
    
    # Check for suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            violations.append(f"Suspicious activity detected: {pattern}")
    
    # If violations found, block the content
    if violations:
        return False, "Content blocked due to security policy violations", violations
    
    return True, text, violations

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Simple Guardrails Validation API",
        "guardrails_loaded": True,
        "validation_type": "rule-based"
    })

@app.route('/validate', methods=['POST'])
def validate_input():
    """
    Validate user input using simple rule-based guardrails
    
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

        # Process input through simple guardrails
        is_valid, filtered_input, violations = simple_guardrails_check(user_input.text)
        
        message = "Input validation passed" if is_valid else "Input blocked by guardrails"
        
        response = ValidationResponse(
            is_valid=is_valid,
            message=message,
            original_input=user_input.text,
            filtered_input=filtered_input if is_valid else "",
            violations=violations
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
        
        # Use simple guardrails check
        is_valid, output_text, violations = simple_guardrails_check(input_text)
        
        if not is_valid:
            output_text = f"Blocked: {'; '.join(violations)}"
        
        return jsonify({
            "valid": is_valid,
            "input": input_text,
            "output": output_text
        })
            
    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return jsonify({
            "valid": False,
            "input": "",
            "output": f"Request error: {str(e)}"
        }), 500

@app.route('/patterns', methods=['GET'])
def get_patterns():
    """
    Get current validation patterns - useful for debugging
    """
    return jsonify({
        "harmful_patterns": HARMFUL_PATTERNS,
        "inappropriate_patterns": INAPPROPRIATE_PATTERNS,
        "suspicious_patterns": SUSPICIOUS_PATTERNS
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Simple Guardrails Validation API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
