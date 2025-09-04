# NanoQuant Core

Extreme LLM Compression Engine - Compress large language models by up to 99.5% without sacrificing quality.

## 🚀 Overview

NanoQuant is an advanced LLM compression system that implements cutting-edge techniques to reduce model sizes while maintaining performance. This repository contains the core compression engine without business logic or monetization features.

## 🔧 Key Features

- **7 Compression Levels**: From light (50% reduction) to atomic (99.5% reduction)
- **Ultra-Advanced Techniques**:
  - UltraSketchLLM (Sub-1-Bit Compression)
  - SliM-LLM (Salience-Driven Mixed-Precision)
  - OneBit (1-Bit Parameter Representation)
  - PTQ1.61 (Sub-2-Bit Quantization)
  - Super Weight Preservation
  - Enhanced SparseGPT & Wanda Pruning
  - CALR (Corrective Adaptive Low-Rank Decomposition)
- **Ollama Integration**: Automatically package and push compressed models
- **Multiple Interfaces**: CLI, Web GUI, and API
- **Hugging Face Support**: Compress any model from the Hub

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/swayam8624/nanoquant-core.git
cd nanoquant-core

# Install dependencies
pip install -r requirements.txt

# Install NanoQuant
pip install -e .
```

## 🖥️ Usage

### CLI Interface

```bash
# Compress a model
nanoquant compress --model "meta-llama/Llama-2-7b-hf" --level "ultra"

# View available compression levels
nanoquant levels

# Analyze a model
nanoquant info --model "meta-llama/Llama-2-7b-hf"
```

### Web Interface

```bash
# Run the web interface
streamlit run nanoquant/web/core_app.py
```

### API Interface

```bash
# Start the API server
uvicorn nanoquant.api.main:app --host 0.0.0.0 --port 8000

# Compress a model via API
curl -X POST "http://localhost:8000/compression/start" \
     -H "Content-Type: application/json" \
     -d '{"model_id": "meta-llama/Llama-2-7b-hf", "compression_level": "ultra"}'
```

## 🧠 Compression Levels

| Level   | Size Reduction | Description                                            |
| ------- | -------------- | ------------------------------------------------------ |
| Light   | 50-70%         | Quality-critical applications                          |
| Medium  | 70-85%         | Balanced compression/quality                           |
| Heavy   | 85-92%         | Significant size reduction                             |
| Extreme | 92-96%         | Maximum compression                                    |
| Ultra   | 96-98%         | Extreme compression with advanced techniques           |
| Nano    | 98-99%         | Sub-1-bit compression                                  |
| Atomic  | 99-99.5%       | Maximum compression with all ultra-advanced techniques |

## 🛠️ Technical Architecture

The core engine consists of several components:

1. **Model Ingestion**: Loads models from Hugging Face or local storage
2. **Compression Engine**: Implements all 7 ultra-advanced compression techniques
3. **NanoQuant Generator**: Creates compressed versions at different levels
4. **Ollama Integration**: Packages models for Ollama distribution
5. **Compression Pipeline**: Orchestrates the entire process

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) (when API is running)
- [Compression Techniques](docs/compression_techniques.md)
- [Usage Examples](docs/examples.md)

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run specific test
pytest tests/test_compression_engine.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of Hugging Face Transformers
- Inspired by research in model compression
- Thanks to the open source community

## 📞 Support

For issues and feature requests, please [open an issue](https://github.com/swayam8624/nanoquant-core/issues).
