"""
Ollama Integration for NanoQuant
Handles packaging and pushing compressed models to Ollama
"""
import os
import subprocess
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class OllamaIntegrationSystem:
    def __init__(self):
        self.ollama_available = self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(["ollama", "--version"],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def package_for_ollama(self, model_path: str,
                          model_name: str,
                          nanoquant_level: str) -> str:
        """
        Package model for Ollama distribution
        Creates a ModelFile and prepares the model for Ollama
        """
        if not self.ollama_available:
            raise RuntimeError("Ollama is not available on this system")
            
        try:
            # Create ModelFile content
            modelfile_content = self._create_modelfile_content(model_path, model_name, nanoquant_level)
            
            # Write ModelFile
            modelfile_path = os.path.join(model_path, "Modelfile")
            with open(modelfile_path, "w") as f:
                f.write(modelfile_content)
            
            logger.info(f"ModelFile created at {modelfile_path}")
            return modelfile_path
        except Exception as e:
            logger.error(f"Error packaging model for Ollama: {e}")
            raise

    def push_to_ollama(self, modelfile_path: str,
                      model_tag: str) -> bool:
        """
        Push model to Ollama using the ModelFile
        """
        if not self.ollama_available:
            raise RuntimeError("Ollama is not available on this system")
            
        try:
            logger.info(f"Pushing model to Ollama with tag: {model_tag}")
            
            # Run ollama create command
            cmd = ["ollama", "create", model_tag, "-f", modelfile_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info(f"Model successfully pushed to Ollama as {model_tag}")
                return True
            else:
                logger.error(f"Failed to push model to Ollama: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Ollama push command timed out")
            return False
        except Exception as e:
            logger.error(f"Error pushing model to Ollama: {e}")
            return False

    def generate_pull_commands(self, model_base_name: str,
                              levels: list) -> Dict[str, str]:
        """
        Generate pull commands for all NanoQuant levels
        """
        commands = {}
        for level in levels:
            tag = f"nanoquant_{model_base_name}:{level}"
            commands[level] = f"ollama pull {tag}"
        return commands

    def _create_modelfile_content(self, model_path: str, model_name: str, nanoquant_level: str) -> str:
        """
        Create ModelFile content for Ollama with proper configuration
        """
        # For a production system, this would convert the model to GGUF format
        # For now, we'll create a basic ModelFile that works with Ollama
        
        modelfile_content = f"""# ModelFile for NanoQuant compressed model
FROM llama3
PARAMETER temperature 0.7
PARAMETER stop Result:
SYSTEM You are a NanoQuant compressed model ({nanoquant_level} level). 
You have been compressed using advanced techniques while maintaining quality.
Model path: {model_path}

# Copy model files
COPY . /model/

# Template for generation
TEMPLATE \"\"\"{{{{ if .System }}}}<<<<START_SYSTEM>>>>{{{{ .System }}}}<<<<END_SYSTEM>>>>{{{{ end }}}}{{{{ if .Prompt }}}}<<<<START_USER>>>>{{{{ .Prompt }}}}<<<<END_USER>>>>{{{{ end }}}}<<<<START_ASSISTANT>>>>{{{{ .Response }}}}<<<<END_ASSISTANT>>>>\"\"\"
"""
        return modelfile_content

    def _convert_to_gguf(self, model_path: str) -> str:
        """
        Convert model to GGUF format for Ollama compatibility
        This is a placeholder - in a real implementation this would use llama.cpp tools
        """
        # In a real implementation, this would:
        # 1. Convert PyTorch model to GGUF format
        # 2. Optimize for inference
        # 3. Return path to converted model
        gguf_path = os.path.join(model_path, "model.gguf")
        # For now, we'll just create an empty file to simulate conversion
        with open(gguf_path, "w") as f:
            f.write("# GGUF model file (simulated)")
        return gguf_path