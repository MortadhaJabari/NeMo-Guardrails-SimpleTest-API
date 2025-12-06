from flask import Flask, request, jsonify
from flask_cors import CORS
from nemoguardrails import LLMRails, RailsConfig
from pydantic import BaseModel, ValidationError
import os
import logging
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Pydantic models for request validation
class ValidationRequest(BaseModel):
    text: str
    user_id: str = "default_user"
    session_id: str = "default_session"

class ValidationResponse(BaseModel):
    is_valid: bool
    message: str
    original_input: str
    filtered_input: str = ""
    violations: list = []

# Initialize NeMo Guardrails
def initialize_guardrails():
    """Initialize NeMo Guardrails configuration for input validation only (no LLM needed)"""
    try:
        # Enhanced Colang configuration for blocking validation
        config = RailsConfig.from_content(
            colang_content="""
# SOAR Command Validation Patterns - Input Rails for Blocking

define user ask malicious command
  "rm -rf"
  "rm -r"
  "delete all"
  "format drive" 
  "shutdown"
  "reboot"
  "dd if="
  "mkfs"
  "fdisk"
  "del /s"
  "deltree"
  "rmdir /s"

define user ask infrastructure attack
  "nmap"
  "sqlmap"
  "hydra"
  "metasploit"
  "burpsuite"
  "dirb"
  "gobuster"
  "nikto"
  "masscan"
  "zmap"
  "fierce"
  "whatweb"
  "wpscan"

define user ask data exfiltration
  "/etc/passwd"
  "/etc/shadow"
  "cat /proc"
  "find / -name"
  "scp"
  "rsync"
  "wget http"
  "curl http"
  "base64"
  "exfiltrat"
  "password dump"
  "credential harvest"

define user ask persistence mechanism
  "crontab"
  "systemctl enable"
  "service"
  "chkconfig"
  ".bashrc"
  ".profile"
  "backdoor"
  "rootkit"
  "adduser"
  "useradd"
  "net user"
  "reg add"

define user ask command injection
  "&&"
  "||" 
  ";"
  "$("
  "`"
  "eval("
  "exec("
  "system("
  "powershell"
  "cmd /c"

# Bot responses that will be returned for blocked inputs
define bot refuse malicious command
  "BLOCKED: Destructive system command detected - cannot assist with operations that could harm infrastructure"

define bot refuse infrastructure attack  
  "BLOCKED: Network attack or vulnerability scanning tool detected - cannot help with unauthorized security testing"

define bot refuse data exfiltration
  "BLOCKED: Data exfiltration attempt detected - cannot assist with unauthorized data access"

define bot refuse persistence mechanism
  "BLOCKED: Persistence mechanism detected - cannot help with installing backdoors"

define bot refuse command injection
  "BLOCKED: Command injection pattern detected - cannot assist with shell manipulation"

define bot inform about safe content
  "Input validation passed - no security violations detected"

# Input validation flows that trigger on user input
define flow malicious command input rail
  user ask malicious command
  bot refuse malicious command
  stop

define flow infrastructure attack input rail
  user ask infrastructure attack
  bot refuse infrastructure attack
  stop

define flow data exfiltration input rail
  user ask data exfiltration
  bot refuse data exfiltration
  stop

define flow persistence mechanism input rail
  user ask persistence mechanism
  bot refuse persistence mechanism
  stop

define flow command injection input rail
  user ask command injection
  bot refuse command injection
  stop

# Default safe content flow
define flow default safe content
  user ...
  bot inform about safe content
            """,
            yaml_content="""
# Configuration for input validation rails - no LLM needed
rails:
  input:
    flows:
      - malicious command input rail
      - infrastructure attack input rail
      - data exfiltration input rail
      - persistence mechanism input rail
      - command injection input rail
      - default safe content
            """
        )
        
        # Initialize rails without LLM for pattern-based validation only
        app.rails = LLMRails(config)
        logger.info("NeMo Guardrails initialized successfully (Colang-based input validation)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize guardrails: {e}")
        app.rails = None
        return False

# Initialize guardrails at module import
initialize_guardrails()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "NeMo Guardrails SOAR Agent Validation API",
        "guardrails_loaded": hasattr(app, 'rails') and app.rails is not None,
        "validation_type": "nemo-guardrails-soar",
        "config_status": "SOAR agent command validation patterns loaded",
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
    """Main validation endpoint for SOAR agent inputs"""
    try:
        # Parse and validate request
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "is_valid": False,
                    "message": "No JSON data provided",
                    "original_input": "",
                    "filtered_input": "",
                    "violations": ["Invalid request format"]
                }), 400
            
            user_input = ValidationRequest(**data)
        except ValidationError as e:
            return jsonify({
                "is_valid": False,
                "message": f"Invalid request format: {e}",
                "original_input": data.get('text', '') if data else '',
                "filtered_input": "",
                "violations": ["Request validation failed"]
            }), 400

        if not hasattr(app, 'rails') or not app.rails:
            return jsonify({
                "is_valid": True,
                "message": "Guardrails not initialized - allowing all input",
                "original_input": user_input.text,
                "filtered_input": user_input.text,
                "violations": []
            })

        # Process input through guardrails (Colang-based validation only)
        try:
            # Use NeMo Guardrails with enhanced Colang patterns
            result = app.rails.generate(
                messages=[{"role": "user", "content": user_input.text}],
                options={
                    "user_id": user_input.user_id,
                    "session_id": user_input.session_id
                }
            )
            
            # Check if input was blocked by Colang patterns
            violations = []
            filtered_input = user_input.text
            is_valid = True
            message = "Input validation passed"
            
            # Check for input rail results in the result object
            if hasattr(result, 'data') and result.data:
                logger.info(f"Result data: {result.data}")
                
            # Check for events or internal state that shows which rail was triggered
            if hasattr(result, '_events') and result._events:
                for event in result._events:
                    logger.info(f"Event: {event}")
                    if hasattr(event, 'flow_id') and 'input rail' in str(event.flow_id):
                        # Input rail was triggered, this means input should be blocked
                        flow_name = str(event.flow_id).replace(' input rail', '')
                        is_valid = False
                        message = f"Input blocked by SOAR Colang security patterns - {flow_name}"
                        filtered_input = f"BLOCKED: {flow_name} detected"
                        violations.append(f"Colang {flow_name} pattern violation detected")
                        break
            
            # Alternative: Check the result's internal rails state
            if hasattr(result, '_state') and hasattr(result._state, '_events'):
                for event in result._state._events:
                    if hasattr(event, 'get') and event.get('type') == 'StartInputRail':
                        flow_id = event.get('flow_id', '')
                        if 'input rail' in flow_id:
                            flow_name = flow_id.replace(' input rail', '')
                            is_valid = False
                            message = f"Input blocked by SOAR Colang security patterns - {flow_name}"
                            filtered_input = f"BLOCKED: {flow_name} detected"
                            violations.append(f"Colang {flow_name} pattern violation detected")
                            break
            
            # Check NeMo Guardrails Colang response (fallback)
            if hasattr(result, 'response') and result.response:
                response_text = str(result.response).strip()
                
                # Check if Colang patterns triggered a blocking response
                blocking_keywords = [
                    "BLOCKED:",
                    "I cannot assist",
                    "I cannot help", 
                    "cannot help with",
                    "cannot assist with",
                    "Destructive system command",
                    "Network attack", 
                    "vulnerability scanning",
                    "Data exfiltration",
                    "unauthorized data access",
                    "Persistence mechanism",
                    "backdoors",
                    "Command injection"
                ]
                
                if any(keyword in response_text for keyword in blocking_keywords):
                    is_valid = False
                    message = "Input blocked by SOAR Colang security patterns"
                    filtered_input = response_text
                    violations.append("Colang security pattern violation detected")
                else:
                    # Input passed validation
                    if is_valid:  # Only set if not already blocked by input rail
                        filtered_input = response_text if response_text else user_input.text
                    
            response = ValidationResponse(
                is_valid=is_valid,
                message=message,
                original_input=user_input.text,
                filtered_input=filtered_input,
                violations=violations
            )

            return jsonify(response.model_dump())

        except Exception as e:
            logger.error(f"NeMo Guardrails validation error: {str(e)}")
            return jsonify({
                "is_valid": False,
                "message": f"Validation processing error: {str(e)}",
                "original_input": user_input.text,
                "filtered_input": "",
                "violations": ["Internal processing error"]
            }), 500

    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return jsonify({
            "is_valid": False,
            "message": f"Request processing error: {str(e)}",
            "original_input": "",
            "filtered_input": "",
            "violations": ["Request processing failed"]
        }), 500

@app.route('/check', methods=['POST'])
def simple_check():
    """Simple validation endpoint for testing"""
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({
                "valid": False,
                "input": "",
                "output": "Missing 'input' field in request"
            }), 400
        
        input_text = data['input']
        
        if not hasattr(app, 'rails') or not app.rails:
            return jsonify({
                "valid": True,
                "input": input_text,
                "output": input_text
            })
        
        try:
            # Use NeMo Guardrails with Colang patterns only
            result = app.rails.generate(
                messages=[{"role": "user", "content": input_text}]
            )
            
            logger.info(f"=== INPUT: {input_text} ===")
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result content: {result}")
            
            # Since result is a dict, check for response content
            response_content = ""
            if isinstance(result, dict):
                # Check various possible keys for response content
                if 'content' in result:
                    response_content = result['content']
                elif 'response' in result:
                    response_content = result['response']
                elif 'role' in result and 'content' in result:
                    # Handle assistant response format: {'role': 'assistant', 'content': ''}
                    response_content = result.get('content', '')
                else:
                    response_content = str(result)
            else:
                response_content = str(result)
                
            logger.info(f"Response content: '{response_content}'")
            
            # Check if Colang patterns triggered a blocking response
            blocking_keywords = [
                "BLOCKED:",
                "I cannot assist",
                "I cannot help", 
                "cannot help with",
                "cannot assist with",
                "Destructive system command",
                "Network attack", 
                "vulnerability scanning",
                "Data exfiltration",
                "unauthorized data access",
                "Persistence mechanism",
                "backdoors",
                "Command injection"
            ]
            
            # If response contains blocking keywords, it was blocked
            if response_content and any(keyword in response_content for keyword in blocking_keywords):
                return jsonify({
                    "valid": False,
                    "input": input_text,
                    "output": response_content,
                    "triggered_rail": "response_blocking"
                })
            
            # New approach: Check for empty content which indicates input rail triggered
            # In input-only mode, when a rail triggers, it results in empty content
            # The result format is {'role': 'assistant', 'content': ''} when blocked
            
            # First check if any of our known malicious patterns are present
            malicious_patterns = ["rm -rf", "del ", "format", "mkfs", "dd if=", "deltree", "rmdir /s"]
            infrastructure_patterns = ["nmap", "sqlmap", "hydra", "metasploit", "burpsuite", "dirb", "gobuster", "nikto"]
            data_exfil_patterns = ["/etc/passwd", "/etc/shadow", "cat /proc", "find / -name", "scp", "rsync", "wget http", "curl http"]
            persistence_patterns = ["crontab", "systemctl enable", "service", "chkconfig", ".bashrc", ".profile", "backdoor"]
            injection_patterns = ["&&", "||", ";", "$(", "`", "eval(", "exec(", "system(", "powershell", "cmd /c"]
            
            # Check if any malicious patterns are detected in the input
            detected_pattern = None
            triggered_rail = None
            
            if any(pattern in input_text.lower() for pattern in malicious_patterns):
                detected_pattern = True
                triggered_rail = "malicious command"
            elif any(pattern in input_text.lower() for pattern in infrastructure_patterns):
                detected_pattern = True
                triggered_rail = "infrastructure attack"
            elif any(pattern in input_text.lower() for pattern in data_exfil_patterns):
                detected_pattern = True
                triggered_rail = "data exfiltration"
            elif any(pattern in input_text.lower() for pattern in persistence_patterns):
                detected_pattern = True
                triggered_rail = "persistence mechanism"
            elif any(pattern in input_text.lower() for pattern in injection_patterns):
                detected_pattern = True
                triggered_rail = "command injection"
            
            # Only treat empty content as blocked if we detected malicious patterns
            # This prevents safe content from being falsely blocked
            if not response_content or response_content.strip() == "":
                if detected_pattern and triggered_rail:
                    # Input rail triggered and we have malicious content - this is a block
                    return jsonify({
                        "valid": False,
                        "input": input_text,
                        "output": f"BLOCKED: {triggered_rail} detected by NeMo Guardrails input validation",
                        "triggered_rail": f"{triggered_rail} input rail"
                    })
                else:
                    # Empty response but no malicious patterns detected - could be safe content that just doesn't generate response
                    # This is normal in input-only mode for safe content
                    pass
            
            # If we get here, input passed all validations
            return jsonify({
                "valid": True,
                "input": input_text,
                "output": response_content if response_content else input_text
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
    app.run(host='0.0.0.0', port=5000, debug=True)