from flask import Flask, render_template, request, jsonify
from litellm import completion
import instructor
from dotenv import load_dotenv
import os
from pathlib import Path
from pass_generator import PassGenerator
from data.models import PassParams

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
LLM_MODEL = "gemini/gemini-2.5-flash-lite"
LLM_INSTRUCTION = Path("data/llm_instruction.md").read_text()

client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
pass_generator = PassGenerator()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_password():
    try:
        user_input = request.json.get("input", "")

        if not user_input.strip():
            return jsonify({"error": "Please enter a description for your password"})

        # Create structured output
        password_config = client.chat.completions.create(
            model=LLM_MODEL,
            api_key=API_KEY,
            messages=[
                {
                    "role": "system",
                    "content": LLM_INSTRUCTION,
                },
                {"role": "user", "content": user_input},
            ],
            response_model=PassParams,
        )

        result = ""
        match password_config.type:
            case "password":
                if password_config.password is not None:
                    result = pass_generator.generate_password(
                        **password_config.password.model_dump()
                    )
                else:
                    return jsonify({"error": "Password parameters missing"})
            case "passphrase":
                if password_config.passphrase is not None:
                    result = pass_generator.generate_passphrase(
                        **password_config.passphrase.model_dump()
                    )
                else:
                    return jsonify({"error": "Passphrase parameters missing"})

        return jsonify({"password": result})

    except Exception as e:
        return jsonify({"error": f"Error generating password: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
