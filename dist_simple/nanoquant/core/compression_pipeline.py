"""
Main Compression Pipeline for NanoQuant
Orchestrates the entire compression process from ingestion to Ollama integration
"""
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CompressionPipeline:
    def __init__(self, output_base_dir: str = "./nanoquants"):
        self.output_base_dir = output_base_dir
        # Import components here to avoid circular imports
        from nanoquant.core.model_ingestion import ModelIngestionPipeline
        from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
        from nanoquant.core.ollama_integration import OllamaIntegrationSystem
        from nanoquant.core.user_management import UserManager

        self.ingestion = ModelIngestionPipeline()
        self.generator = UltraNanoQuantGenerator()
        self.ollama = OllamaIntegrationSystem()
        self.user_manager = UserManager()

        # Create base directory
        os.makedirs(self.output_base_dir, exist_ok=True)

    def process_model(self, model_id: str,
                     compression_level: str = "medium",
                     dataset_path: str = None,
                     push_to_ollama: bool = True,
                     user_id: str = None,
                     knowledge_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete pipeline: ingest, compress, evaluate, and package
        """
        logger.info(f"Processing model: {model_id} with compression level: {compression_level}")

        # Check user credits for paid tiers
        if user_id and not self._check_user_access(user_id, compression_level):
            raise PermissionError(f"Insufficient credits or access for compression level: {compression_level}")

        # Step 1: Ingest model
        logger.info("Step 1: Ingesting model...")
        model_artifacts = self.ingestion.ingest_model(model_id)

        # Step 2: Generate NanoQuants
        logger.info("Step 2: Generating NanoQuants...")
        model_name = model_id.replace("/", "_")
        output_dir = os.path.join(self.output_base_dir, model_name)
        generated_models = self.generator.generate_nanoquants(model_artifacts, output_dir)

        # Step 3: Apply knowledge tuning if provided
        if knowledge_data:
            logger.info("Step 3: Applying knowledge tuning...")
            from nanoquant.core.knowledge_tuning import KnowledgeTuningEngine
            tuner = KnowledgeTuningEngine()
            
            # Tune each generated model
            tuned_models = []
            for model_info in generated_models:
                try:
                    tuned_result = tuner.tune_model_with_knowledge(
                        model_info["path"],
                        knowledge_data,
                        "text"  # Default to text tuning
                    )
                    tuned_models.append({
                        "original": model_info,
                        "tuned": tuned_result
                    })
                except Exception as e:
                    logger.error(f"Error tuning model {model_info['path']}: {e}")
                    tuned_models.append({
                        "original": model_info,
                        "tuned": None,
                        "error": str(e)
                    })
            
            # Update generated models with tuning info
            generated_models = tuned_models

        # Step 4: Package for Ollama
        ollama_tags = []
        if push_to_ollama and self.ollama.ollama_available:
            logger.info("Step 4: Packaging for Ollama...")
            for model_info in generated_models:
                # Handle both tuned and non-tuned models
                if isinstance(model_info, dict) and "tuned" in model_info:
                    # This is a tuned model
                    model_path = model_info["tuned"]["tuned_model_path"] if model_info["tuned"] else model_info["original"]["path"]
                    level = model_info["original"]["level"]
                else:
                    # This is a regular model
                    model_path = model_info["path"]
                    level = model_info["level"]
                    
                tag = f"nanoquant_{model_name}:{level}"
                try:
                    modelfile_path = self.ollama.package_for_ollama(
                        model_path, model_name, level
                    )
                    # Push to Ollama
                    if self.ollama.push_to_ollama(modelfile_path, tag):
                        ollama_tags.append(tag)
                        logger.info(f"Successfully pushed {tag} to Ollama")
                    else:
                        logger.error(f"Failed to push {tag} to Ollama")
                except Exception as e:
                    logger.error(f"Error packaging {level} NanoQuant: {e}")
        elif push_to_ollama:
            logger.warning("Ollama not available, skipping Ollama integration")

        # Generate pull commands
        pull_commands = self.ollama.generate_pull_commands(
            model_name,
            [m["level"] for m in generated_models] if isinstance(generated_models[0], dict) and "level" in generated_models[0] else 
            [m["original"]["level"] for m in generated_models if isinstance(m, dict) and "original" in m]
        )

        # Deduct credits if user_id is provided
        if user_id:
            self._deduct_user_credits(user_id, compression_level)

        return {
            "model_id": model_id,
            "generated_models": generated_models,
            "output_directory": output_dir,
            "ollama_tags": ollama_tags,
            "pull_commands": pull_commands
        }

    def process_custom_model(self, model_id: str,
                           custom_config: Dict[str, Any],
                           dataset_path: str = None,
                           push_to_ollama: bool = True,
                           user_id: str = None,
                           knowledge_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a model with custom compression configuration
        """
        logger.info(f"Processing model with custom config: {model_id}")

        # Check user credits for paid tiers
        if user_id and not self._check_user_access(user_id, "custom"):
            raise PermissionError(f"Insufficient credits or access for custom compression")

        # Step 1: Ingest model
        logger.info("Step 1: Ingesting model...")
        model_artifacts = self.ingestion.ingest_model(model_id)

        # Step 2: Generate custom NanoQuant
        logger.info("Step 2: Generating custom NanoQuant...")
        model_name = model_id.replace("/", "_")
        output_dir = os.path.join(self.output_base_dir, model_name)
        
        custom_model = self.generator.generate_custom_nanoquant(
            model_artifacts, output_dir, custom_config, "custom"
        )

        # Step 3: Apply knowledge tuning if provided
        if knowledge_data:
            logger.info("Step 3: Applying knowledge tuning...")
            from nanoquant.core.knowledge_tuning import KnowledgeTuningEngine
            tuner = KnowledgeTuningEngine()
            
            try:
                tuned_result = tuner.tune_model_with_knowledge(
                    custom_model["path"],
                    knowledge_data,
                    "text"  # Default to text tuning
                )
                custom_model["tuned"] = tuned_result
            except Exception as e:
                logger.error(f"Error tuning custom model: {e}")
                custom_model["tuning_error"] = str(e)

        # Step 4: Package for Ollama
        ollama_tags = []
        if push_to_ollama and self.ollama.ollama_available:
            logger.info("Step 4: Packaging for Ollama...")
            model_path = custom_model.get("tuned", {}).get("tuned_model_path", custom_model["path"]) if custom_model.get("tuned") else custom_model["path"]
            tag = f"nanoquant_{model_name}:custom"
            try:
                modelfile_path = self.ollama.package_for_ollama(
                    model_path, model_name, "custom"
                )
                # Push to Ollama
                if self.ollama.push_to_ollama(modelfile_path, tag):
                    ollama_tags.append(tag)
                    logger.info(f"Successfully pushed {tag} to Ollama")
                else:
                    logger.error(f"Failed to push {tag} to Ollama")
            except Exception as e:
                logger.error(f"Error packaging custom NanoQuant: {e}")
        elif push_to_ollama:
            logger.warning("Ollama not available, skipping Ollama integration")

        # Deduct credits if user_id is provided
        if user_id:
            self._deduct_user_credits(user_id, "custom")

        return {
            "model_id": model_id,
            "custom_model": custom_model,
            "output_directory": output_dir,
            "ollama_tags": ollama_tags
        }

    def get_compression_levels(self) -> Dict[str, Any]:
        """
        Get information about available compression levels
        """
        from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
        generator = UltraNanoQuantGenerator()
        return generator.compression_levels

    def _check_user_access(self, user_id: str, compression_level: str) -> bool:
        """
        Check if user has access to the requested compression level
        """
        return self.user_manager.check_compression_access(user_id, compression_level)

    def _deduct_user_credits(self, user_id: str, compression_level: str) -> bool:
        """
        Deduct credits from user account based on compression level
        """
        # Define credit costs for different levels
        level_costs = {
            "light": 0,
            "medium": 0,
            "heavy": 10,
            "extreme": 25,
            "ultra": 50,
            "nano": 100,
            "atomic": 200,
            "custom": 75
        }
        
        cost = level_costs.get(compression_level, 0)
        
        if cost > 0:
            # Check if user is on free tier and using a trial
            user_profile = self.user_manager.get_user_profile(user_id)
            if user_profile and user_profile.get("tier") == "free":
                # Check if this is a trial usage
                trials_used = self.user_manager._get_trials_count(user_id, compression_level)
                if trials_used < 2:  # Still within trial limit
                    self.user_manager.increment_trial_usage(user_id, compression_level)
                    logger.info(f"Free tier trial used for {compression_level} compression")
                    return True
            
            # Deduct actual credits
            success = self.user_manager.deduct_credits(user_id, cost, f"compression_{compression_level}")
            if success:
                logger.info(f"Deducted {cost} credits from user {user_id} for {compression_level} compression")
            else:
                logger.warning(f"Failed to deduct {cost} credits from user {user_id}")
            return success
        
        return True