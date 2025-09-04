"""
Streamlit web interface for NanoQuant
Provides a user-friendly GUI for model compression
"""
import streamlit as st
import requests
import time
import os
import json
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="NanoQuant - LLM Compression",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    [data-testid=stSidebar] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid #334155;
    }
    
    /* Main content area */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Card styling */
    div[data-testid="stHorizontalBlock"] > div {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 15px;
        border: 1px solid #334155;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Primary button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        font-size: 18px;
        padding: 15px 30px;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Input fields */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div,
    .stTextArea>div>div>textarea {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid #334155;
        border-radius: 8px;
        color: #f8fafc;
        font-size: 16px;
    }
    
    /* Progress bar */
    .stProgress>div>div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    
    /* Success box */
    .success-box {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        color: #6ee7b7;
    }
    
    /* Warning box */
    .warning-box {
        background: rgba(251, 191, 36, 0.15);
        border: 1px solid #fbbf24;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        color: #fde68a;
    }
    
    /* Error box */
    .error-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        color: #fca5a5;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(30, 58, 138, 0.5);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #334155;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: rgba(15, 23, 42, 0.7);
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3b82f6;
        border-radius: 4px;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #bfdbfe;
    }
    
    /* Login form */
    .login-form {
        max-width: 400px;
        margin: 0 auto;
        padding: 30px;
        background: rgba(30, 41, 59, 0.8);
        border-radius: 15px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Social login buttons */
    .social-login-btn {
        width: 100%;
        margin: 10px 0;
        padding: 12px;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .google-btn {
        background: #4285f4;
        color: white;
    }
    
    .github-btn {
        background: #333;
        color: white;
    }
    
    .social-login-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Payment buttons */
    .payment-method {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .payment-method:hover {
        background: rgba(56, 70, 109, 0.8);
        transform: translateY(-2px);
    }
    
    .payment-method.selected {
        border: 2px solid #3b82f6;
        background: rgba(59, 130, 246, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'payment_intent' not in st.session_state:
    st.session_state.payment_intent = None

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

def login_user(email, password):
    """Login user and store session token"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            st.session_state.user_token = data["session_token"]
            st.session_state.user_id = data["user_id"]
            # Get user profile
            get_user_profile()
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error during login: {e}")
        return False

def register_user(email, password):
    """Register new user"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            st.session_state.user_token = data["session_token"]
            st.session_state.user_id = data["user_id"]
            st.success("Registration successful!")
            # Get user profile
            get_user_profile()
            return True
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error during registration: {e}")
        return False

def social_login(provider):
    """Initiate social login"""
    try:
        response = requests.get(f"{API_BASE_URL}/auth/social/{provider}")
        if response.status_code == 200:
            auth_url = response.json()["auth_url"]
            st.markdown(f"[Login with {provider.capitalize()}]({auth_url})", unsafe_allow_html=True)
            st.info(f"Click the link above to login with {provider.capitalize()}")
        else:
            st.error(f"Failed to initiate {provider} login")
    except Exception as e:
        st.error(f"Error initiating {provider} login: {e}")

def get_user_profile():
    """Get user profile information"""
    if not st.session_state.user_token:
        return None
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        response = requests.get(f"{API_BASE_URL}/user/profile", headers=headers)
        if response.status_code == 200:
            st.session_state.user_profile = response.json()
            return st.session_state.user_profile
        else:
            st.error("Failed to get user profile")
            return None
    except Exception as e:
        st.error(f"Error getting user profile: {e}")
        return None

def redeem_coupon(coupon_code):
    """Redeem coupon code"""
    if not st.session_state.user_token:
        st.error("Please login first")
        return False
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        response = requests.post(f"{API_BASE_URL}/coupons/redeem", 
                                json={"coupon_code": coupon_code},
                                headers=headers)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Coupon redeemed! {result['credits_added']} credits added.")
            # Refresh user profile
            get_user_profile()
            return True
        else:
            st.error(f"Failed to redeem coupon: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error redeeming coupon: {e}")
        return False

def create_payment(amount, currency, payment_method):
    """Create a payment for credits"""
    if not st.session_state.user_token:
        st.error("Please login first")
        return None
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method
        }
        response = requests.post(f"{API_BASE_URL}/payments/create", 
                                json=payload,
                                headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Payment creation failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error creating payment: {e}")
        return None

def start_compression(model_id, compression_level, preserve_super_weights, push_to_ollama):
    """Start model compression"""
    if not st.session_state.user_token:
        st.error("Please login first")
        return None
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        payload = {
            "model_id": model_id,
            "compression_level": compression_level,
            "preserve_super_weights": preserve_super_weights,
            "push_to_ollama": push_to_ollama
        }
        response = requests.post(f"{API_BASE_URL}/compression/start", 
                                json=payload,
                                headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Compression failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error during compression: {e}")
        return None

def get_compression_levels():
    """Get available compression levels"""
    if not st.session_state.user_token:
        return {}
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        response = requests.get(f"{API_BASE_URL}/compression-levels", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to get compression levels")
            return {}
    except Exception as e:
        st.error(f"Error getting compression levels: {e}")
        return {}

def main():
    # Add a decorative header
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: rgba(30, 41, 59, 0.8); border-radius: 15px; margin-bottom: 30px; border: 1px solid #334155;">
        <h1>🚀 NanoQuant - Extreme LLM Compression</h1>
        <p style="font-size: 1.3em; color: #cbd5e1;">Compress large language models into extremely small versions without sacrificing quality</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user is logged in
    if not st.session_state.user_token:
        # Show login/registration page
        show_auth_page()
    else:
        # Show main application
        show_main_app()

def show_auth_page():
    """Show authentication page (login/registration)"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #f8fafc;'>🔐 User Authentication</h2>", unsafe_allow_html=True)
        
        auth_option = st.radio("Choose an option:", ["Login", "Register"])
        
        if auth_option == "Login":
            email = st.text_input("Email", key="auth_email")
            password = st.text_input("Password", type="password", key="auth_password")
            
            if st.button("Login", type="primary", key="login_btn"):
                if email and password:
                    if login_user(email, password):
                        st.success("Login successful!")
                        st.experimental_rerun()
                else:
                    st.warning("Please enter both email and password")
            
            st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Or login with:</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Google", key="google_login"):
                    social_login("google")
            with col2:
                if st.button("GitHub", key="github_login"):
                    social_login("github")
        else:
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            
            if st.button("Register", type="primary", key="register_btn"):
                if email and password and confirm_password:
                    if password == confirm_password:
                        if register_user(email, password):
                            st.success("Registration successful!")
                            st.experimental_rerun()
                    else:
                        st.warning("Passwords do not match")
                else:
                    st.warning("Please fill in all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_main_app():
    """Show main application interface"""
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown("<h2>👤 User Profile</h2>", unsafe_allow_html=True)
        
        if st.session_state.user_profile:
            st.markdown(f"<p><strong>Email:</strong> {st.session_state.user_profile['email']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>Credits:</strong> {st.session_state.user_profile['credits']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>Tier:</strong> {st.session_state.user_profile['tier'].capitalize()}</p>", unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Profile"):
            get_user_profile()
            st.experimental_rerun()
        
        if st.button("💳 Buy Credits"):
            st.session_state.show_payment = True
            st.experimental_rerun()
        
        if st.button("🎟️ Redeem Coupon"):
            st.session_state.show_coupon = True
            st.experimental_rerun()
        
        if st.button("🧠 Knowledge Tuning"):
            st.session_state.show_knowledge_tuning = True
            st.experimental_rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.user_token = None
            st.session_state.user_profile = None
            st.session_state.show_payment = False
            st.session_state.show_coupon = False
            st.session_state.show_knowledge_tuning = False
            st.experimental_rerun()
    
    # Show payment or coupon modals if requested
    if "show_payment" in st.session_state and st.session_state.show_payment:
        show_payment_modal()
        return
    
    if "show_coupon" in st.session_state and st.session_state.show_coupon:
        show_coupon_modal()
        return
    
    if "show_knowledge_tuning" in st.session_state and st.session_state.show_knowledge_tuning:
        show_knowledge_tuning_modal()
        return
    
    # Main content
    st.markdown("<h2>🎯 Model Compression</h2>", unsafe_allow_html=True)
    
    # Get compression levels
    compression_data = get_compression_levels()
    levels = compression_data.get("levels", {}) if compression_data else {}
    
    # Model selection
    col1, col2 = st.columns(2)
    
    with col1:
        model_id = st.text_input("Model ID", placeholder="e.g., meta-llama/Llama-2-7b-hf", 
                                help="Enter a Hugging Face model ID or local path")
    
    with col2:
        # Filter accessible levels
        accessible_levels = {k: v for k, v in levels.items() if v.get("accessible", False)}
        if not accessible_levels:
            accessible_levels = levels  # Fallback to all levels if filtering fails
        
        level_names = list(accessible_levels.keys())
        level_display = [f"{lvl} - {accessible_levels[lvl]['name']}" for lvl in level_names]
        
        compression_level = st.selectbox(
            "Compression Level", 
            level_names,
            format_func=lambda x: f"{accessible_levels[x]['name']} ({accessible_levels[x]['description']})",
            help="Select the compression level"
        )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            preserve_super_weights = st.checkbox("Preserve Super Weights", 
                                                help="Preserve critical parameters that disproportionately affect model behavior")
            push_to_ollama = st.checkbox("Push to Ollama", value=True,
                                        help="Automatically push compressed model to Ollama")
        
        with col2:
            st.info(f"Selected level cost: {levels.get(compression_level, {}).get('cost', 0)} credits")
            if st.session_state.user_profile:
                st.info(f"Your credits: {st.session_state.user_profile['credits']}")
    
    # Compression button
    if st.button("🚀 Compress Model", type="primary", use_container_width=True):
        if not model_id:
            st.warning("Please enter a model ID")
        else:
            with st.spinner("Compressing model... This may take several minutes"):
                result = start_compression(
                    model_id, 
                    compression_level, 
                    preserve_super_weights, 
                    push_to_ollama
                )
                
                if result:
                    st.success("Compression completed successfully!")
                    
                    # Display results
                    st.markdown("<h3>📊 Compression Results</h3>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Original Model", model_id, "")
                    col2.metric("Compression Level", compression_level, "")
                    col3.metric("Models Generated", len(result["generated_models"]), "")
                    
                    # Ollama instructions
                    if result["ollama_tags"]:
                        st.markdown("<h4>📦 Ollama Models</h4>", unsafe_allow_html=True)
                        for tag in result["ollama_tags"]:
                            st.code(f"ollama pull {tag}", language="bash")
                        
                        st.markdown("<h4>🏃 Running Compressed Models</h4>", unsafe_allow_html=True)
                        for tag, command in result["pull_commands"].items():
                            st.code(command, language="bash")
    
    # Information section
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>📚 About NanoQuant</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <p>NanoQuant implements cutting-edge compression techniques to reduce LLM sizes by up to 99.5% while maintaining quality:</p>
        <ul>
            <li>UltraSketchLLM - Sub-1-Bit Compression</li>
            <li>SliM-LLM - Salience-Driven Mixed-Precision</li>
            <li>OneBit - 1-Bit Parameter Representation</li>
            <li>PTQ1.61 - Sub-2-Bit Quantization</li>
            <li>Super Weight Preservation</li>
            <li>Enhanced SparseGPT & Wanda Pruning</li>
            <li>CALR - Corrective Adaptive Low-Rank Decomposition</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_payment_modal():
    """Show payment modal for buying credits"""
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); z-index: 1000; display: flex; justify-content: center; align-items: center;">
        <div style="background: #1e293b; border-radius: 15px; padding: 30px; width: 500px; max-width: 90%; border: 1px solid #334155;">
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #f8fafc;'>💳 Buy Credits</h2>", unsafe_allow_html=True)
    
    # Credit packages
    credit_packages = [
        {"credits": 100, "price": 10, "currency": "USD", "description": "Basic Package"},
        {"credits": 250, "price": 25, "currency": "USD", "description": "Standard Package"},
        {"credits": 500, "price": 50, "currency": "USD", "description": "Premium Package"},
        {"credits": 1000, "price": 100, "currency": "USD", "description": "Enterprise Package"}
    ]
    
    # Payment methods
    payment_methods = ["stripe", "razorpay", "paypal"]
    payment_method_names = ["Credit Card (Stripe)", "UPI/Bank Transfer (Razorpay)", "PayPal"]
    
    # Select credit package
    st.markdown("<h3>Select Credit Package</h3>", unsafe_allow_html=True)
    selected_package = st.selectbox(
        "Credit Package",
        range(len(credit_packages)),
        format_func=lambda x: f"{credit_packages[x]['credits']} credits - ${credit_packages[x]['price']} ({credit_packages[x]['description']})"
    )
    
    # Select payment method
    st.markdown("<h3>Select Payment Method</h3>", unsafe_allow_html=True)
    selected_method = st.radio("Payment Method", range(len(payment_methods)), 
                              format_func=lambda x: payment_method_names[x])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirm Payment"):
            package = credit_packages[selected_package]
            method = payment_methods[selected_method]
            
            # Create payment
            payment = create_payment(package["price"] * 100, package["currency"], method)
            if payment:
                st.session_state.payment_intent = payment
                st.success("Payment created successfully!")
                if payment.get("payment_url"):
                    st.markdown(f"[Proceed to Payment]({payment['payment_url']})", unsafe_allow_html=True)
                else:
                    st.info("Please complete the payment using the provided details")
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_payment = False
            st.experimental_rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def show_coupon_modal():
    """Show coupon redemption modal"""
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); z-index: 1000; display: flex; justify-content: center; align-items: center;">
        <div style="background: #1e293b; border-radius: 15px; padding: 30px; width: 500px; max-width: 90%; border: 1px solid #334155;">
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #f8fafc;'>🎟️ Redeem Coupon</h2>", unsafe_allow_html=True)
    
    coupon_code = st.text_input("Coupon Code", placeholder="Enter your coupon code")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Redeem Coupon"):
            if coupon_code:
                if redeem_coupon(coupon_code):
                    st.session_state.show_coupon = False
                    st.experimental_rerun()
            else:
                st.warning("Please enter a coupon code")
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_coupon = False
            st.experimental_rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# Add knowledge tuning function after the main function
def tune_model_knowledge(model_id, knowledge_data, tuning_type="text"):
    """Tune a model with domain-specific knowledge"""
    if not st.session_state.user_token:
        st.error("Please login first")
        return None
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        payload = {
            "model_id": model_id,
            "knowledge_data": knowledge_data,
            "tuning_type": tuning_type
        }
        response = requests.post(f"{API_BASE_URL}/tuning/knowledge", 
                                json=payload,
                                headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Knowledge tuning failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error during knowledge tuning: {e}")
        return None
