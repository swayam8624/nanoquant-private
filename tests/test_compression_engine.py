"""
Unit tests for the NanoQuant compression engine
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestCompressionEngine(unittest.TestCase):
    """Test cases for the compression engine"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    def test_imports(self):
        """Test that we can import the core modules"""
        try:
            from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
            from nanoquant.core.model_ingestion import ModelIngestionPipeline
            from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
            from nanoquant.core.ollama_integration import OllamaIntegrationSystem
            from nanoquant.core.compression_pipeline import CompressionPipeline
        except ImportError as e:
            self.fail(f"Failed to import core modules: {e}")

    def test_compression_engine_initialization(self):
        """Test that the compression engine can be initialized"""
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        try:
            engine = UltraAdvancedCompressionEngine()
            self.assertIsNotNone(engine)
        except Exception as e:
            self.fail(f"Failed to initialize compression engine: {e}")

    def test_model_ingestion_initialization(self):
        """Test that the model ingestion pipeline can be initialized"""
        from nanoquant.core.model_ingestion import ModelIngestionPipeline
        try:
            ingestion = ModelIngestionPipeline()
            self.assertIsNotNone(ingestion)
        except Exception as e:
            self.fail(f"Failed to initialize model ingestion pipeline: {e}")

    def test_nanoquant_generator_initialization(self):
        """Test that the NanoQuant generator can be initialized"""
        from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
        try:
            generator = UltraNanoQuantGenerator()
            self.assertIsNotNone(generator)
        except Exception as e:
            self.fail(f"Failed to initialize NanoQuant generator: {e}")

    def test_ollama_integration_initialization(self):
        """Test that the Ollama integration system can be initialized"""
        from nanoquant.core.ollama_integration import OllamaIntegrationSystem
        try:
            ollama = OllamaIntegrationSystem()
            self.assertIsNotNone(ollama)
        except Exception as e:
            self.fail(f"Failed to initialize Ollama integration system: {e}")

    def test_compression_pipeline_initialization(self):
        """Test that the compression pipeline can be initialized"""
        from nanoquant.core.compression_pipeline import CompressionPipeline
        try:
            pipeline = CompressionPipeline()
            self.assertIsNotNone(pipeline)
        except Exception as e:
            self.fail(f"Failed to initialize compression pipeline: {e}")

if __name__ == '__main__':
    unittest.main()