# PasaiGen - AI Password Generator

An AI-powered password and passphrase generator that understands natural language descriptions.

## Features

- 🎯 Natural language input - describe what you need in plain English
- 🔐 Strong password generation with customizable character sets
- 📚 Passphrase generation with word-based security
- ⚡ Easy-to-read or easy-to-type options
- 🛡️ Secure random generation using cryptographic functions
- 🌐 Beautiful Streamlit web interface

## Installation

1. Clone the repository
2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Create a `.env` file with your API key:
   ```
   API_KEY=your_api_key_here
   ```

## Usage

### Web Interface (Streamlit)
Run the interactive web interface:
```bash
uv run streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

### Command Line
Run the original command-line version:
```bash
uv run python app.py
```

## Examples

You can describe your password needs in natural language:

- "Generate a 16-character password with uppercase, lowercase, numbers, and symbols that's easy to type"
- "Create a passphrase with 4 words separated by dashes"
- "Make a strong 20-character password for my bank account"
- "Generate a gaming password that's 12 characters with numbers"

## Requirements

- Python 3.12+
- API key for the LLM service
- Internet connection for AI processing