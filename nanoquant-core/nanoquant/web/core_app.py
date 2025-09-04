"""
Streamlit web interface for NanoQuant (Core Version)
Provides a user-friendly GUI for model compression without business logic
"""
import streamlit as st
import time
import os
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
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'compression_result' not in st.session_state:
    st.session_state.compression_result = None

def start_compression(model_id, compression_level, push_to_ollama):
    """Start model compression (simulated)"""
    try:
        # Import the compression pipeline
        from nanoquant.core.compression_pipeline import CompressionPipeline
        
        # Create pipeline
        pipeline = CompressionPipeline()
        
        # Process model (this would be the actual compression)
        result = pipeline.process_model(
            model_id=model_id,
            compression_level=compression_level,
            push_to_ollama=push_to_ollama
        )
        
        return result
    except Exception as e:
        st.error(f"Error during compression: {e}")
        return None

def main():
    # Add a decorative header
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: rgba(30, 41, 59, 0.8); border-radius: 15px; margin-bottom: 30px; border: 1px solid #334155;">
        <h1>🚀 NanoQuant - Extreme LLM Compression</h1>
        <p style="font-size: 1.3em; color: #cbd5e1;">Compress large language models into extremely small versions without sacrificing quality</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("<h2>ℹ️ About NanoQuant</h2>", unsafe_allow_html=True)
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
        
        st.markdown("<h3>📚 Compression Levels</h3>", unsafe_allow_html=True)
        st.info("""
        - Light: 50-70% size reduction
        - Medium: 70-85% size reduction
        - Heavy: 85-92% size reduction
        - Extreme: 92-96% size reduction
        - Ultra: 96-98% size reduction
        - Nano: 98-99% size reduction
        - Atomic: 99-99.5% size reduction
        """)
    
    # Main content
    st.markdown("<h2>🎯 Model Compression</h2>", unsafe_allow_html=True)
    
    # Model selection
    col1, col2 = st.columns(2)
    
    with col1:
        model_id = st.text_input("Model ID", placeholder="e.g., meta-llama/Llama-2-7b-hf", 
                                help="Enter a Hugging Face model ID or local path")
    
    with col2:
        compression_level = st.selectbox(
            "Compression Level", 
            ["light", "medium", "heavy", "extreme", "ultra", "nano", "atomic"],
            help="Select the compression level"
        )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        push_to_ollama = st.checkbox("Push to Ollama", value=True,
                                    help="Automatically push compressed model to Ollama")
    
    # Compression button
    if st.button("🚀 Compress Model", type="primary", use_container_width=True):
        if not model_id:
            st.warning("Please enter a model ID")
        else:
            with st.spinner("Compressing model... This may take several minutes"):
                result = start_compression(
                    model_id, 
                    compression_level, 
                    push_to_ollama
                )
                
                if result:
                    st.session_state.compression_result = result
                    st.success("Compression completed successfully!")
    
    # Display results if available
    if st.session_state.compression_result:
        st.markdown("<h3>📊 Compression Results</h3>", unsafe_allow_html=True)
        
        result = st.session_state.compression_result
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Original Model", result["model_id"], "")
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

if __name__ == "__main__":
    main()