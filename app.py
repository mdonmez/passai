"""
Pass Generator Flask Application

A modern web application for generating secure passwords and passphrases
using AI-powered parameter extraction and customizable generation options.
"""

import logging
import os
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import instructor
from litellm import completion

from pass_generator import PassGenerator
from data.models import PassParams

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Configuration from environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("API_KEY environment variable is required")
    raise ValueError("API_KEY environment variable must be set")

LLM_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash-lite")
LLM_INSTRUCTION_PATH = Path("data/llm_instruction.md")

# Load LLM instruction template
try:
    LLM_INSTRUCTION = LLM_INSTRUCTION_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    logger.error(f"LLM instruction file not found: {LLM_INSTRUCTION_PATH}")
    raise

# Initialize services
client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
pass_generator = PassGenerator()


@app.route("/")
def index():
    """Render the main application page."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_pass():
    """
    Generate a password or passphrase based on user input.

    Returns:
        JSON response with generated pass or error message
    """
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        user_input = data.get("input", "").strip()

        if not user_input:
            return jsonify({"error": "Please enter a description for your pass"}), 400

        # Generate pass configuration using LLM
        logger.info(f"Processing request for input: {user_input[:50]}...")

        pass_config = client.chat.completions.create(
            model=LLM_MODEL,
            api_key=API_KEY,
            messages=[
                {"role": "system", "content": LLM_INSTRUCTION},
                {"role": "user", "content": user_input},
            ],
            response_model=PassParams,
        )

        # Generate pass based on configuration
        result = ""

        match pass_config.type:
            case "password":
                if pass_config.password is not None:
                    result = pass_generator.generate_password(
                        **pass_config.password.model_dump()
                    )
                else:
                    return jsonify({"error": "Pass parameters missing"}), 400

            case "passphrase":
                if pass_config.passphrase is not None:
                    result = pass_generator.generate_passphrase(
                        **pass_config.passphrase.model_dump()
                    )
                else:
                    return jsonify({"error": "Passphrase parameters missing"}), 400

            case _:
                return jsonify({"error": "Invalid pass type specified"}), 400

        logger.info("Successfully generated pass")
        return jsonify({"pass": result})

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400

    except Exception as e:
        logger.error(f"Error generating pass: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to generate pass. Please try again."}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Development server configuration
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    logger.info(
        f"Starting application in {'debug' if debug_mode else 'production'} mode"
    )
    app.run(host=host, port=port, debug=debug_mode)
