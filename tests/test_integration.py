"""
Integration tests for the NanoQuant system
"""
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestNanoQuantIntegration(unittest.TestCase):
    """Integration tests for the NanoQuant system"""

    def test_full_pipeline_imports(self):
        """Test that all components of the full pipeline can be imported"""
        try:
            # Core components
            from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
            from nanoquant.core.model_ingestion import ModelIngestionPipeline
            from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
            from nanoquant.core.ollama_integration import OllamaIntegrationSystem
            from nanoquant.core.compression_pipeline import CompressionPipeline
            
            # Interface components
            from nanoquant.api.main import app as api_app
            from nanoquant.cli.main import app as cli_app
            from nanoquant.web.app import main as web_app_main
            
        except ImportError as e:
            self.fail(f"Failed to import components: {e}")

    def test_component_initialization(self):
        """Test that all components can be initialized"""
        # Core components
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        from nanoquant.core.model_ingestion import ModelIngestionPipeline
        from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
        from nanoquant.core.ollama_integration import OllamaIntegrationSystem
        from nanoquant.core.compression_pipeline import CompressionPipeline
        
        try:
            engine = UltraAdvancedCompressionEngine()
            ingestion = ModelIngestionPipeline()
            generator = UltraNanoQuantGenerator()
            ollama = OllamaIntegrationSystem()
            pipeline = CompressionPipeline()
            
            # Verify objects are created
            self.assertIsNotNone(engine)
            self.assertIsNotNone(ingestion)
            self.assertIsNotNone(generator)
            self.assertIsNotNone(ollama)
            self.assertIsNotNone(pipeline)
            
        except Exception as e:
            self.fail(f"Failed to initialize components: {e}")

if __name__ == '__main__':
    unittest.main()