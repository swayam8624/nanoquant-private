# NanoQuant Core

Extreme LLM Compression Engine - Compress large language models by up to 99.5%

## 🚀 Overview

NanoQuant is an advanced compression engine that reduces the size of large language models while maintaining their performance. This repository contains the core compression technology that powers the full NanoQuant system.

## 🎯 Features

- **7 Compression Levels**: From light (50% reduction) to atomic (99.5% reduction)
- **Ultra-Advanced Techniques**: 
  - UltraSketchLLM (Sub-1-Bit)
  - SliM-LLM (Mixed-Precision)
  - OneBit (1-Bit Parameters)
  - PTQ1.61 (Sub-2-Bit)
  - Super Weight Preservation
- **Universal Compatibility**: Works with any Hugging Face model
- **Ollama Integration**: Push compressed models directly to Ollama
- **Multi-Interface**: CLI, Web, and API access

## 📦 Installation

```bash
pip install nanoquant-core
```

Or install from source:

```bash
git clone https://github.com/swayam8624/nanoquant-core.git
cd nanoquant-core
pip install -e .
```

## 🖥️ Usage

### CLI

```bash
# Compress a model
nanoquant compress --model "meta-llama/Llama-2-7b-hf" --level "ultra"

# View compression levels
nanoquant levels

# Analyze a model
nanoquant info --model "meta-llama/Llama-2-7b-hf"
```

### Web Interface

```bash
streamlit run nanoquant/web/core_app.py
```

### API

```bash
uvicorn nanoquant.api.main:app --host 0.0.0.0 --port 8000
```

Then visit `http://localhost:8000/docs` for API documentation.

## 🛠️ Compression Levels

| Level | Size Reduction | Use Case |
|-------|----------------|----------|
| Light | 50-70% | Initial experimentation |
| Medium | 70-85% | Development and testing |
| Heavy | 85-92% | Production deployment |
| Extreme | 92-96% | Edge devices |
| Ultra | 96-98% | Mobile deployment |
| Nano | 98-99% | Minimal resource environments |
| Atomic | 99-99.5% | Ultra-constrained devices |

## 🤝 Contributing

We welcome contributions to the core compression technology! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Full NanoQuant System](https://github.com/swayam8624/Nanoquant) - Complete system with business features
