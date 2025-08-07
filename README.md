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