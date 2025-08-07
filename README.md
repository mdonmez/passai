# PasaiGen - AI Password Generator

An AI-powered password and passphrase generator that understands natural language descriptions and creates secure passwords through an intuitive web interface.

## Features

- 🎯 **Natural Language Input** - Simply describe what you need in plain English
- 🔐 **Strong Password Generation** - Customizable character sets and complexity
- 📚 **Passphrase Generation** - Word-based security with configurable separators
- ⚡ **Accessibility Options** - Easy-to-read or easy-to-type modes
- 🛡️ **Cryptographically Secure** - Uses secure random generation
- 🌐 **Modern Web Interface** - Clean, responsive Flask-based UI
- 🤖 **AI-Powered** - Understands complex password requirements

## Quick Start

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd passgen
   pip install flask instructor[litellm] litellm python-dotenv streamlit
   ```

2. **Configure API**
   Create a `.env` file with your API key:
   ```
   API_KEY=your_api_key_here
   ```

3. **Run Web Interface**
   ```bash
   python flask_app.py
   ```
   
   Open your browser to `http://localhost:5000`

## Usage Examples

Simply describe your password requirements in natural language:

- *"Generate a 16-character password with uppercase, lowercase, numbers, and symbols that's easy to type"*
- *"Create a passphrase with 4 words separated by dashes"*
- *"Make a strong 20-character password for my bank account"*
- *"Generate a gaming password that's 12 characters with numbers"*
- *"Simple PIN with 6 digits"*
- *"Corporate password, 15 chars, all types, easy to read"*

## Alternative Interfaces

### Streamlit Web App
For an alternative web interface:
```bash
streamlit run streamlit_app.py
```
Then open `http://localhost:8501`

### Command Line
For direct command-line usage:
```bash
python app.py
```

## Requirements

- **Python 3.12+**
- **LLM API Key** (for AI processing)
- **Internet Connection** (for AI requests)

## How It Works

1. **Describe** your password needs in natural language
2. **AI Processing** converts your description to technical parameters
3. **Secure Generation** creates cryptographically strong passwords
4. **Instant Results** with automatic clipboard copying (web interface)

## Operation Logic: Under the Hood

PasaiGen seamlessly translates your plain English request into a secure password or passphrase by following a precise, multi-step process:

1.  **Natural Language Input**: Your request (e.g., *"a 15-character password for my bank that's easy to read"*) is sent to the backend.
2.  **AI Instruction**: The system loads a detailed instruction prompt from `data/llm_instruction.md`. This prompt guides the Large Language Model (LLM) on how to interpret the request and what kind of structured data to return.
3.  **Structured AI Processing**: Using the `instructor` and `litellm` libraries, the request is sent to the LLM. `instructor` forces the LLM to respond with a clean, validated JSON object that conforms to the Pydantic models in `data/models.py`. This is the core of the AI translation, turning your text into a machine-readable format like:
    ```json
    {
      "type": "password",
      "password": {
        "length": 15,
        "easy_to": "read"
      }
    }
    ```
4.  **Parameter Dispatch**: The application inspects the `type` field from the AI's response. It then dispatches the structured parameters to the appropriate function in `pass_generator.py`—either `generate_password` or `generate_passphrase`.
5.  **Cryptographically Secure Generation**: The `PassGenerator` class uses Python's `secrets` module to build the final output. This module is specifically designed for generating cryptographically strong random numbers, ensuring that character and word selection is unpredictable and secure.
6.  **Constraint Enforcement**: The generator strictly adheres to all parameters received from the AI, such as length, character types (uppercase, numbers, etc.), minimum counts, and accessibility options (`easy_to_read` or `easy_to_type`), which intelligently filter out ambiguous characters like '1', 'l', and 'I'.
7.  **Final Output**: The resulting secure password or passphrase is sent back to the user interface.