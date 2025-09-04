"""
Model Ingestion Pipeline for NanoQuant
Handles loading models from Hugging Face Hub or local storage
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelIngestionPipeline:
    def __init__(self):
        self.supported_architectures = {
            "gpt2": {"family": "gpt", "default_target_modules": ["c_attn"]},
            "llama": {"family": "llama", "default_target_modules": ["q_proj", "v_proj"]},
            "mistral": {"family": "mistral", "default_target_modules": ["q_proj", "v_proj"]},
            "falcon": {"family": "falcon", "default_target_modules": ["query_key_value"]},
            "opt": {"family": "opt", "default_target_modules": ["q_proj", "k_proj", "v_proj"]},
            "phi": {"family": "phi", "default_target_modules": ["q_proj", "k_proj", "v_proj"]},
            "gemma": {"family": "gemma", "default_target_modules": ["q_proj", "v_proj"]},
        }

    def analyze_model(self, model_id: str) -> Dict[str, Any]:
        """
        Analyze model architecture and recommend compression strategy
        """
        logger.info(f"Analyzing model: {model_id}")
        # Load model config to determine architecture
        try:
            from transformers import AutoConfig
            config = AutoConfig.from_pretrained(model_id)
        except Exception as e:
            logger.error(f"Failed to load model config for {model_id}: {e}")
            # Fallback config
            config = type('Config', (), {'model_type': 'generic', 'hidden_size': 768, 'num_hidden_layers': 12})()

        # Determine model family
        model_family = self._identify_model_family(config)

        # Get recommended target modules for LoRA
        target_modules = self.supported_architectures.get(
            model_family,
            {"default_target_modules": ["q_proj", "v_proj"]}
        )["default_target_modules"]

        # Extract model parameters
        hidden_size = getattr(config, 'hidden_size', None)
        num_layers = getattr(config, 'num_hidden_layers', None)
        vocab_size = getattr(config, 'vocab_size', None)

        return {
            "model_id": model_id,
            "architecture": getattr(config, 'model_type', 'unknown'),
            "model_family": model_family,
            "target_modules": target_modules,
            "hidden_size": hidden_size,
            "num_layers": num_layers,
            "vocab_size": vocab_size,
            "recommended_compression": self._recommend_compression(config)
        }

    def ingest_model(self, model_id: str, cache_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest model from Hugging Face Hub with optimal settings
        """
        logger.info(f"Ingesting model: {model_id}")
        # Analyze model first
        model_info = self.analyze_model(model_id)

        # Determine optimal dtype based on model size and device
        device = self._get_device()
        torch_dtype = self._determine_optimal_dtype(model_info, device)

        # Load model with memory optimization
        logger.info(f"Loading model with dtype: {torch_dtype} on device: {device}")
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                cache_dir=cache_dir,
                trust_remote_code=True  # Allow custom models
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

        # Load tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir, trust_remote_code=True)
            # Add pad token if it doesn't exist
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            logger.info("Tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}")
            raise

        # Move to device
        model.to(device)

        return {
            "model": model,
            "tokenizer": tokenizer,
            "info": model_info,
            "device": device,
            "torch_dtype": torch_dtype
        }

    def ingest_local_model(self, model_path: str) -> Dict[str, Any]:
        """
        Ingest model from local storage
        """
        logger.info(f"Ingesting local model from: {model_path}")
        
        # Determine optimal dtype based on device
        device = self._get_device()
        
        # Load model
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            logger.info("Local model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            raise

        # Load tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            # Add pad token if it doesn't exist
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            logger.info("Local tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local tokenizer: {e}")
            raise

        # Move to device
        model.to(device)

        # Create basic model info
        model_info = {
            "model_id": os.path.basename(model_path),
            "architecture": "unknown",
            "model_family": "generic",
            "target_modules": ["q_proj", "v_proj"],
            "hidden_size": None,
            "num_layers": None,
            "vocab_size": None,
            "recommended_compression": {"compression_level": "medium"}
        }

        return {
            "model": model,
            "tokenizer": tokenizer,
            "info": model_info,
            "device": device,
            "torch_dtype": torch.float16 if device.type != "cpu" else torch.float32
        }

    def _identify_model_family(self, config) -> str:
        """Identify model family from config"""
        model_type = getattr(config, 'model_type', 'generic').lower()
        for family in self.supported_architectures:
            if family in model_type:
                return family
        return "generic"

    def _recommend_compression(self, config) -> Dict[str, Any]:
        """Recommend compression strategy based on model characteristics"""
        hidden_size = getattr(config, 'hidden_size', 768)
        num_layers = getattr(config, 'num_hidden_layers', 12)

        # Size-based recommendations
        if hidden_size > 4096 or num_layers > 32:
            return {
                "compression_level": "extreme",
                "quantization_bits": 4,
                "pruning_ratio": 0.7,
                "lora_r": 8,
                "reason": "Large model detected - recommending aggressive compression"
            }
        elif hidden_size > 2048 or num_layers > 24:
            return {
                "compression_level": "heavy",
                "quantization_bits": 8,
                "pruning_ratio": 0.5,
                "lora_r": 16,
                "reason": "Medium-large model detected - recommending moderate compression"
            }
        else:
            return {
                "compression_level": "medium",
                "quantization_bits": 8,
                "pruning_ratio": 0.3,
                "lora_r": 32,
                "reason": "Small model detected - recommending balanced compression"
            }

    def _get_device(self) -> torch.device:
        """Get optimal device"""
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("Using MPS device")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU device")
        return device

    def _determine_optimal_dtype(self, model_info: Dict, device: torch.device) -> torch.dtype:
        """Determine optimal dtype based on device and model"""
        # For large models, use float16/bfloat16 to save memory
        hidden_size = model_info.get("hidden_size", 768)
        
        if device.type == "cuda":
            # Use bfloat16 if available (Ampere+ GPUs), otherwise float16
            if torch.cuda.is_bf16_supported():
                return torch.bfloat16
            else:
                return torch.float16
        elif device.type == "mps":
            return torch.float16
        else:
            # For CPU, use bfloat16 if available, otherwise float32
            if hasattr(torch, 'bfloat16'):
                return torch.bfloat16
            return torch.float32