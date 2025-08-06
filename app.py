from litellm import completion
import instructor
from dotenv import load_dotenv
import os
from pathlib import Path
from pass_generator import PassGenerator
from data.models import PassParams

load_dotenv()

API_KEY = os.getenv("API_KEY")
LLM_MODEL = "gemini/gemini-2.5-flash-lite"
LLM_INSTRUCTION = Path("data/llm_instruction.md").read_text()


client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
pass_generator = PassGenerator()

USER_INPUT = "Generate a strong password with at least 12 characters, including uppercase, lowercase, numbers, and special characters. Make it easy to read but hard to guess."

# Create structured output
password_config = client.chat.completions.create(
    model=LLM_MODEL,
    api_key=API_KEY,
    messages=[
        {
            "role": "system",
            "content": LLM_INSTRUCTION,
        },
        {"role": "user", "content": USER_INPUT},
    ],
    response_model=PassParams,
)

match password_config.type:
    case "password":
        if password_config.password is not None:
            password = pass_generator.generate_password(
                **password_config.password.model_dump()
            )
            print(f"Generated Password: {password}")
        else:
            print("Password parameters missing.")
    case "passphrase":
        if password_config.passphrase is not None:
            passphrase = pass_generator.generate_passphrase(
                **password_config.passphrase.model_dump()
            )
            print(f"Generated Passphrase: {passphrase}")
        else:
            print("Passphrase parameters missing.")
