import streamlit as st
from litellm import completion
import instructor
from dotenv import load_dotenv
import os
from pathlib import Path
from pass_generator import PassGenerator
from data.models import PassParams
import time

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY")
LLM_MODEL = "gemini/gemini-2.5-flash-lite"
LLM_INSTRUCTION = Path("data/llm_instruction.md").read_text()


# Initialize components
@st.cache_resource
def get_client():
    return instructor.from_litellm(completion, mode=instructor.Mode.JSON)


@st.cache_resource
def get_pass_generator():
    return PassGenerator()


def generate_password_or_passphrase(user_input: str) -> str:
    """Generate password or passphrase based on user input using LLM."""
    client = get_client()
    pass_generator = get_pass_generator()

    if not API_KEY:
        st.error(
            "API_KEY not found in environment variables. Please check your .env file."
        )
        return ""

    try:
        # Create structured output using LLM
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
        print("[LLM Response] password_config:", password_config)
        # Generate based on type
        match password_config.type:
            case "password":
                if password_config.password is not None:
                    print("[Password Params]", password_config.password.model_dump())
                    result = pass_generator.generate_password(
                        **password_config.password.model_dump()
                    )
                    print("[Generated Password]", result)
                    return result
                else:
                    st.error("Password parameters missing.")
                    return ""
            case "passphrase":
                if password_config.passphrase is not None:
                    print(
                        "[Passphrase Params]", password_config.passphrase.model_dump()
                    )
                    result = pass_generator.generate_passphrase(
                        **password_config.passphrase.model_dump()
                    )
                    print("[Generated Passphrase]", result)
                    return result
                else:
                    st.error("Passphrase parameters missing.")
                    return ""
    except Exception as e:
        st.error(f"Error generating password: {str(e)}")
        print("[Error]", str(e))
        return ""


def main():
    st.set_page_config(
        page_title="PasaiGen - AI Password Generator", page_icon="🔐", layout="centered"
    )

    st.title("🔐 PasaiGen")
    st.subheader("AI-Powered Password & Passphrase Generator")

    st.markdown("""
    Generate strong, customized passwords and passphrases using natural language descriptions.
    Simply describe what kind of password you need, and our AI will create it for you!
    """)

    # Input section
    st.markdown("### 📝 Describe your password needs")

    # Initialize session state
    if "last_input" not in st.session_state:
        st.session_state.last_input = ""
    if "generated_password" not in st.session_state:
        st.session_state.generated_password = ""
    if "input_timer" not in st.session_state:
        st.session_state.input_timer = None
    if "should_generate" not in st.session_state:
        st.session_state.should_generate = False

    user_input = st.text_area(
        "Describe your password requirements:",
        placeholder="E.g., Generate a 15-character password with uppercase, lowercase, numbers, and symbols that's easy to read...",
        height=100,
        key="password_input",
    )

    # Add JavaScript to continuously monitor input and force auto-refresh
    st.markdown(
        """
    <script>
    let lastKnownValue = '';
    let monitoringActive = true;
    
    function startInputMonitoring() {
        if (!monitoringActive) return;
        
        // Find the textarea
        const textArea = window.parent.document.querySelector('textarea[data-testid="stTextArea"]') ||
                        window.parent.document.querySelector('textarea[aria-label*="password"]') ||
                        window.parent.document.querySelector('textarea');
        
        if (textArea) {
            const currentValue = textArea.value.trim();
            
            // Check if value changed
            if (currentValue !== lastKnownValue) {
                lastKnownValue = currentValue;
                
                // Store in localStorage for persistence
                localStorage.setItem('pasaigen_live_input', currentValue);
                localStorage.setItem('pasaigen_input_timestamp', Date.now().toString());
                
                // Force Streamlit to refresh by triggering a fake event
                textArea.dispatchEvent(new Event('input', { bubbles: true }));
                textArea.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Also try to trigger Streamlit's state update
                if (window.parent.streamlitSetComponentValue) {
                    window.parent.streamlitSetComponentValue('live_input_monitor', currentValue);
                }
            }
        }
        
        // Continue monitoring every 100ms
        setTimeout(startInputMonitoring, 100);
    }
    
    // Start monitoring after a short delay
    setTimeout(startInputMonitoring, 200);
    
    // Also monitor on page events
    window.parent.document.addEventListener('keyup', startInputMonitoring);
    window.parent.document.addEventListener('input', startInputMonitoring);
    </script>
    """,
        unsafe_allow_html=True,
    )

    # Get current input value
    current_input = user_input.strip() if user_input else ""

    # Force continuous refresh when there's input
    if current_input:
        # Auto-refresh every 100ms to catch live changes
        time.sleep(0.1)
        st.rerun()

    # Check if input changed
    if st.session_state.last_input != current_input:
        st.session_state.last_input = current_input
        # Reset timer when input changes
        if current_input:  # Only start timer if there's actual input
            st.session_state.input_timer = time.time()
            st.session_state.should_generate = False
            st.session_state.generated_password = ""  # Clear previous result
        else:
            st.session_state.input_timer = None
            st.session_state.should_generate = False
            st.session_state.generated_password = ""

    # Auto-generate logic (only if there's input)
    if current_input:
        # Check if timer exceeds 2 seconds
        if (
            st.session_state.input_timer is not None
            and time.time() - st.session_state.input_timer >= 2
            and not st.session_state.should_generate
        ):
            st.session_state.should_generate = True
            # Generate password
            with st.spinner("🤖 AI is generating your password..."):
                result = generate_password_or_passphrase(current_input)

            if result:
                st.session_state.generated_password = result

        # Display result if we have one
        if st.session_state.generated_password:
            st.markdown("### 🎉 Generated Result")
            st.code(st.session_state.generated_password, language=None)
            st.success("✅ Password generated! Select and copy the text above.")

    # Auto-refresh mechanism - always run to continuously check
    if current_input and st.session_state.input_timer is not None:
        elapsed_time = time.time() - st.session_state.input_timer
        if elapsed_time < 2 and not st.session_state.should_generate:
            # Show countdown
            remaining = 2 - elapsed_time
            st.info(f"⏳ Generating in {remaining:.1f} seconds...")
            time.sleep(0.1)
            st.rerun()

    # Information section
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        **PasaiGen** uses AI to understand your natural language description and generate 
        passwords or passphrases that match your specific requirements.
        
        **Features:**
        - 🎯 Natural language input - just describe what you need
        - 🔐 Strong password generation with customizable character sets
        - 📚 Passphrase generation with word-based security
        - ⚡ Easy-to-read or easy-to-type options
        - 🛡️ Secure random generation using cryptographic functions
        
        **Examples of what you can ask for:**
        - "16-character password with symbols but easy to type"
        - "Passphrase with 4 words separated by underscores"
        - "Strong password for banking with all character types"
        - "Gaming password that's 12 chars with numbers"
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>🔐 Built with Streamlit | Keep your passwords secure!</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
