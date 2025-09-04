"""
Multi-Level NanoQuant Generation with Ultra-Advanced Techniques
"""
import os
import torch
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class UltraNanoQuantGenerator:
    def __init__(self):
        # Updated compression levels that leverage ultra-advanced techniques
        self.compression_levels = {
            "light": {
                "description": "50-70% size reduction with maximum quality preservation",
                "quantization": {"type": "8bit"},
                "pruning": {"type": "wanda", "ratio": 0.15},  # Reduced pruning for quality preservation
                "lora": {"r": 64, "alpha": 32, "dropout": 0.05}
            },
            "medium": {
                "description": "70-85% size reduction with balanced compression/quality",
                "quantization": {"type": "8bit"},
                "pruning": {"type": "wanda", "ratio": 0.3},
                "lora": {"r": 32, "alpha": 32, "dropout": 0.1}
            },
            "heavy": {
                "description": "85-92% size reduction with significant compression",
                "quantization": {"type": "4bit"},
                "pruning": {"type": "sparsegpt", "ratio": 0.5},  # SparseGPT for one-shot pruning
                "decomposition": {"type": "low_rank", "rank_ratio": 0.6},  # Low-rank decomposition
                "lora": {"r": 16, "alpha": 16, "dropout": 0.15}
            },
            "extreme": {
                "description": "92-96% size reduction with maximum compression",
                "quantization": {"type": "quip"},  # QuIP for 2-bit quantization
                "pruning": {"type": "sparsegpt", "ratio": 0.7},
                "decomposition": {"type": "calr", "rank_ratio": 0.4},  # CALR decomposition
                "lora": {"r": 8, "alpha": 8, "dropout": 0.2}
            },
            "ultra": {
                "description": "96-98% size reduction using advanced techniques",
                "quantization": {"type": "aqlm"},  # AQLM for extreme quantization
                "pruning": {"type": "sparsegpt", "ratio": 0.85},
                "decomposition": {"type": "calr", "rank_ratio": 0.25},
                "preserve_super_weights": True,  # Preserve super weights as per Apple's research
                "lora": {"r": 4, "alpha": 4, "dropout": 0.25}
            },
            "nano": {
                "description": "98-99% size reduction using ultra-advanced techniques",
                "quantization": {"type": "ptq1_61"},  # PTQ1.61 for sub-2-bit quantization
                "pruning": {"type": "sparsegpt", "ratio": 0.92},
                "decomposition": {"type": "calr", "rank_ratio": 0.15},
                "preserve_super_weights": True,  # Preserve super weights as per Apple's research
                "lora": {"r": 2, "alpha": 2, "dropout": 0.3}
            },
            "atomic": {
                "description": "Maximum compression using all ultra-advanced techniques",
                "quantization": {"type": "ultrasketch"},  # UltraSketchLLM for sub-1-bit quantization
                "pruning": {"type": "sparsegpt", "ratio": 0.95},
                "decomposition": {"type": "calr", "rank_ratio": 0.1},
                "preserve_super_weights": True,
                "lora": {"r": 1, "alpha": 1, "dropout": 0.35}
            }
        }

    def generate_nanoquants(self, model_artifacts: Dict[str, Any],
                           output_dir: str) -> List[Dict[str, Any]]:
        """
        Generate multiple NanoQuants at different compression levels including ultra-advanced levels
        """
        generated_models = []

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate NanoQuant for each compression level
        for level_name, config in self.compression_levels.items():
            logger.info(f"Generating {level_name} NanoQuant ({config['description']})...")

            # Create compression engine
            from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
            compressor = UltraAdvancedCompressionEngine()

            # Apply compression
            compressed_artifacts = compressor.compress_model(model_artifacts, config)

            # Save model
            model_name = f"{model_artifacts['info']['model_id'].replace('/', '_')}_{level_name}"
            model_path = os.path.join(output_dir, model_name)

            self._save_model(compressed_artifacts, model_path)
            generated_models.append({
                "name": model_name,
                "level": level_name,
                "path": model_path,
                "description": config["description"],
                "compression_ratio": self._estimate_compression_ratio(level_name),
                "config": config
            })

            logger.info(f"{level_name} NanoQuant saved to {model_path}")

        return generated_models

    def generate_custom_nanoquant(self, model_artifacts: Dict[str, Any],
                                output_dir: str,
                                custom_config: Dict[str, Any],
                                name: str = "custom") -> Dict[str, Any]:
        """
        Generate a custom NanoQuant with user-specified compression techniques
        """
        logger.info(f"Generating custom NanoQuant with config: {custom_config}")

        # Create compression engine
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        compressor = UltraAdvancedCompressionEngine()

        # Apply compression
        compressed_artifacts = compressor.compress_model(model_artifacts, custom_config)

        # Save model
        model_name = f"{model_artifacts['info']['model_id'].replace('/', '_')}_{name}"
        model_path = os.path.join(output_dir, model_name)

        self._save_model(compressed_artifacts, model_path)

        return {
            "name": model_name,
            "path": model_path,
            "config": custom_config
        }

    def _save_model(self, compressed_artifacts: Dict[str, Any], path: str):
        """Save compressed model with proper error handling"""
        model = compressed_artifacts["model"]
        tokenizer = compressed_artifacts["tokenizer"]

        os.makedirs(path, exist_ok=True)

        # Save model
        try:
            # For PEFT models, we need to merge and unload
            if hasattr(model, 'merge_and_unload'):
                logger.info("Merging LoRA weights before saving...")
                merged_model = model.merge_and_unload()
                merged_model.save_pretrained(path)
            else:
                model.save_pretrained(path)
            logger.info(f"Model saved successfully to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            # Fallback: save state dict
            try:
                torch.save(model.state_dict(), os.path.join(path, "pytorch_model.bin"))
                logger.info("Fallback model save successful")
            except Exception as e2:
                logger.error(f"Fallback model save also failed: {e2}")

        # Save tokenizer
        try:
            tokenizer.save_pretrained(path)
            logger.info(f"Tokenizer saved successfully to {path}")
        except Exception as e:
            logger.error(f"Error saving tokenizer: {e}")

    def _estimate_compression_ratio(self, level_name: str) -> float:
        """
        Estimate compression ratio for a given level
        """
        ratios = {
            "light": 0.3,
            "medium": 0.15,
            "heavy": 0.08,
            "extreme": 0.04,
            "ultra": 0.02,
            "nano": 0.01,
            "atomic": 0.005
        }
        ratio = ratios.get(level_name, 0.1)
        logger.info(f"Estimated compression ratio for {level_name}: {ratio*100:.1f}%")
        return ratio

    def get_level_info(self, level_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific compression level
        """
        if level_name in self.compression_levels:
            return self.compression_levels[level_name]
        else:
            raise ValueError(f"Unknown compression level: {level_name}")

    def list_levels(self) -> List[str]:
        """
        List all available compression levels
        """
        return list(self.compression_levels.keys())