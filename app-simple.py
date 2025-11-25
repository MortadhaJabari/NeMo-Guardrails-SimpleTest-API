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

# SOAR/Agent execution validation patterns for automated security operations
# Patterns designed to detect malicious automated instructions and agent commands

# Malicious system commands and destructive operations
MALICIOUS_COMMAND_PATTERNS = [
    r'\brm\s+-rf\s+/',                    # Destructive file deletion
    r'\bformat\s+[c-z]:',                 # Windows disk formatting
    r'\bdel\s+/[sq]\s+\*',               # Windows bulk deletion
    r'\bmkfs\.',                          # Filesystem formatting
    r'\bdd\s+if=/dev/zero',               # Disk wiping
    r'\bsudo\s+rm\s+-rf',                 # Privileged deletion
    r'\bshutdown\s+[-/][srhf]',          # System shutdown/restart
    r'\bkillall\s+-9',                    # Process termination
    r'\bchmod\s+777\s+/',                 # Dangerous permission changes
]

# Network and infrastructure attacks through agents
INFRASTRUCTURE_ATTACK_PATTERNS = [
    r'\bnmap\s+-s[STAUF]',               # Stealth network scanning
    r'\bhydra\s+.*-l\s+.*-P',            # Password brute forcing
    r'\bsqlmap\s+.*--dump',              # Database dumping
    r'\bmetasploit\b.*\bexploit\b',      # Exploit framework usage
    r'\bnc\s+-[el]\s+.*\d+',             # Netcat backdoors
    r'\bwget\s+.*\|.*sh',                # Download and execute
    r'\bcurl\s+.*\|\s*bash',             # Remote script execution
    r'\bpowershell\s+.*-encodedcommand', # Obfuscated PowerShell
    r'\bbase64\s+-d.*\|\s*sh',           # Decoded script execution
]

# Data exfiltration and credential theft
DATA_EXFILTRATION_PATTERNS = [
    r'\bfind\s+.*-name.*passwd',         # Password file searching
    r'\bgrep\s+-r.*password',            # Password hunting
    r'\bscp\s+.*root@',                  # Suspicious file transfer
    r'\brsync\s+.*:/etc/',               # System config exfiltration
    r'\btar\s+.*\|\s*nc',                # Data compression and transfer
    r'\bzip\s+.*shadow\b',               # Password file compression
    r'\bcp\s+/etc/passwd',               # System file copying
    r'\bcat\s+/etc/shadow',              # Password hash reading
]

# Persistence and backdoor installation
PERSISTENCE_PATTERNS = [
    r'\bcrontab\s+-e',                   # Scheduled task creation
    r'\bsystemctl\s+.*enable',           # Service installation
    r'\bchkconfig\s+.*on',               # Service auto-start
    r'\becho\s+.*>>\s*/etc/',            # System config modification
    r'\bchmod\s+\+s\s+',                 # SUID bit setting
    r'\buseradd\s+.*-o\s+-u\s+0',       # Root user creation
    r'\bmkdir.*\.ssh.*authorized_keys',  # SSH key backdoor
    r'\bssh-keygen\b.*\bauthorized_keys', # SSH persistence
]

# Command injection and code execution attempts
INJECTION_PATTERNS = [
    r';\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=',   # Command chaining with assignment
    r'\$\([^)]+\)',                      # Command substitution
    r'`[^`]+`',                          # Backtick command execution
    r'&&\s*[a-zA-Z_]',                   # Command chaining
    r'\|\|\s*[a-zA-Z_]',                 # OR command chaining
    r'>\s*/dev/tcp/',                    # TCP redirection
    r'exec\s*\(',                       # Direct execution
    r'eval\s*\(',                       # Dynamic evaluation
    r'system\s*\(',                     # System call
]

def simple_guardrails_check(text: str) -> tuple[bool, str, List[str]]:
    """
    SOAR/Agent instruction validation for automated security operations
    Detects malicious commands, injections, and dangerous operations
    Returns: (is_valid, filtered_text, violations)
    """
    text_lower = text.lower()
    violations = []
    
    # Check for malicious system commands
    for pattern in MALICIOUS_COMMAND_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(f"Malicious command detected: {pattern}")
    
    # Check for infrastructure attacks
    for pattern in INFRASTRUCTURE_ATTACK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(f"Infrastructure attack detected: {pattern}")
    
    # Check for data exfiltration attempts
    for pattern in DATA_EXFILTRATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(f"Data exfiltration attempt detected: {pattern}")
    
    # Check for persistence mechanisms
    for pattern in PERSISTENCE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(f"Persistence mechanism detected: {pattern}")
    
    # Check for command injection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(f"Command injection detected: {pattern}")
    
    # If violations found, block the content
    if violations:
        return False, "SOAR instruction blocked due to security policy violations", violations
    
    return True, text, violations

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SOAR Agent Command Validation API",
        "guardrails_loaded": True,
        "validation_type": "soar-agent-protection",
        "pattern_categories": [
            "malicious_commands",
            "infrastructure_attacks", 
            "data_exfiltration",
            "persistence_mechanisms",
            "command_injection"
        ]
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
    Get current SOAR/Agent validation patterns - useful for debugging
    """
    return jsonify({
        "malicious_command_patterns": MALICIOUS_COMMAND_PATTERNS,
        "infrastructure_attack_patterns": INFRASTRUCTURE_ATTACK_PATTERNS,
        "data_exfiltration_patterns": DATA_EXFILTRATION_PATTERNS,
        "persistence_patterns": PERSISTENCE_PATTERNS,
        "injection_patterns": INJECTION_PATTERNS
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Simple Guardrails Validation API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
