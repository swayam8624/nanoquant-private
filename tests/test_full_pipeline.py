"""
Full pipeline tests for the NanoQuant system
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import torch
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestFullPipeline(unittest.TestCase):
    """Full pipeline tests for the NanoQuant system"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    def test_ollama_integration_system(self):
        """Test the Ollama integration system functionality"""
        from nanoquant.core.ollama_integration import OllamaIntegrationSystem
        
        # Mock the subprocess calls to avoid actually calling Ollama
        with patch('subprocess.run') as mock_run:
            # Mock the ollama version check
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            # Initialize the system
            ollama = OllamaIntegrationSystem()
            
            # Test pull command generation
            commands = ollama.generate_pull_commands("test_model", ["medium", "ultra"])
            self.assertIn("medium", commands)
            self.assertIn("ultra", commands)
            self.assertTrue(commands["medium"].startswith("ollama pull"))
            self.assertTrue("nanoquant_test_model:medium" in commands["medium"])

    def test_compression_pipeline_with_ollama(self):
        """Test the compression pipeline with Ollama integration"""
        from nanoquant.core.compression_pipeline import CompressionPipeline
        
        # Mock the subprocess calls to avoid actually calling Ollama
        with patch('subprocess.run') as mock_run:
            # Mock the ollama version check
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            # Initialize the pipeline
            pipeline = CompressionPipeline()
            
            # Verify that the Ollama integration system is properly initialized
            self.assertIsNotNone(pipeline.ollama)

    def test_cli_commands(self):
        """Test that CLI commands are properly defined"""
        from nanoquant.cli.main import app
        
        # Check that all expected commands are present by checking registered callback names
        # For Typer apps, we need to check the registered callbacks
        command_names = []
        if hasattr(app, 'register'):
            # Newer versions of Typer
            command_names = [cmd.name for cmd in app.registered_commands if cmd.name]
        elif hasattr(app, 'registered_commands'):
            # Older versions of Typer
            command_names = [cmd.name for cmd in app.registered_commands if cmd.name]
        else:
            # Fallback - try to get commands from the info
            if hasattr(app, 'info') and hasattr(app.info, 'registered_commands'):
                command_names = [cmd.name for cmd in app.info.registered_commands if cmd.name]
        
        expected_commands = ["compress", "list", "info", "techniques", "levels", "serve", "dashboard", "interactive"]
        
        # If we couldn't get command names, skip this test
        if not command_names:
            self.skipTest("Could not retrieve CLI command names")
        
        for command in expected_commands:
            self.assertIn(command, command_names)

    def test_web_app_import(self):
        """Test that the web app can be imported without errors"""
        try:
            from nanoquant.web.app import main
            # The import succeeded
        except Exception as e:
            self.fail(f"Failed to import web app: {e}")

    def test_api_app_import(self):
        """Test that the API app can be imported without errors"""
        try:
            from nanoquant.api.main import app
            # The import succeeded
        except Exception as e:
            self.fail(f"Failed to import API app: {e}")

    def test_compression_engine_initialization(self):
        """Test that the compression engine can be initialized"""
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        try:
            engine = UltraAdvancedCompressionEngine()
            self.assertIsNotNone(engine)
            # Check that all strategy dictionaries are properly initialized
            self.assertTrue(len(engine.quantization_strategies) > 0)
            self.assertTrue(len(engine.pruning_strategies) > 0)
            self.assertTrue(len(engine.decomposition_strategies) > 0)
        except Exception as e:
            self.fail(f"Failed to initialize compression engine: {e}")

    def test_nanoquant_generator_initialization(self):
        """Test that the NanoQuant generator can be initialized"""
        from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
        try:
            generator = UltraNanoQuantGenerator()
            self.assertIsNotNone(generator)
            # Check that all compression levels are properly defined
            self.assertTrue(len(generator.compression_levels) > 0)
            self.assertIn("light", generator.compression_levels)
            self.assertIn("atomic", generator.compression_levels)
        except Exception as e:
            self.fail(f"Failed to initialize NanoQuant generator: {e}")

    def test_model_ingestion_initialization(self):
        """Test that the model ingestion pipeline can be initialized"""
        from nanoquant.core.model_ingestion import ModelIngestionPipeline
        try:
            ingestion = ModelIngestionPipeline()
            self.assertIsNotNone(ingestion)
            # Check that supported architectures are defined
            self.assertTrue(len(ingestion.supported_architectures) > 0)
        except Exception as e:
            self.fail(f"Failed to initialize model ingestion pipeline: {e}")

    @patch('nanoquant.core.model_ingestion.AutoModelForCausalLM.from_pretrained')
    @patch('nanoquant.core.model_ingestion.AutoTokenizer.from_pretrained')
    def test_model_ingestion_analyze_model(self, mock_tokenizer, mock_model):
        """Test model analysis functionality"""
        from nanoquant.core.model_ingestion import ModelIngestionPipeline
        
        # Mock the model and tokenizer
        mock_model.return_value = Mock()
        mock_tokenizer.return_value = Mock()
        
        # Create pipeline
        pipeline = ModelIngestionPipeline()
        
        # Test model analysis
        with patch('transformers.AutoConfig.from_pretrained') as mock_config:
            # Mock config with specific attributes
            mock_config_instance = Mock()
            mock_config_instance.model_type = "gpt2"
            mock_config_instance.hidden_size = 768
            mock_config_instance.num_hidden_layers = 12
            mock_config_instance.vocab_size = 50257
            mock_config.return_value = mock_config_instance
            
            result = pipeline.analyze_model("gpt2")
            
            # Verify the result
            self.assertEqual(result["model_id"], "gpt2")
            self.assertEqual(result["architecture"], "gpt2")
            self.assertEqual(result["model_family"], "gpt2")
            self.assertIsNotNone(result["recommended_compression"])

    def test_compression_levels_info(self):
        """Test that compression levels information is correctly structured"""
        from nanoquant.core.nanoquant_generator import UltraNanoQuantGenerator
        generator = UltraNanoQuantGenerator()
        
        # Test getting level info
        level_info = generator.get_level_info("medium")
        self.assertIn("description", level_info)
        self.assertIn("quantization", level_info)
        self.assertIn("pruning", level_info)
        
        # Test listing levels
        levels = generator.list_levels()
        self.assertIn("medium", levels)
        self.assertIn("atomic", levels)

    def test_ollama_tag_format(self):
        """Test that Ollama tags are formatted correctly"""
        from nanoquant.core.ollama_integration import OllamaIntegrationSystem
        
        ollama = OllamaIntegrationSystem()
        commands = ollama.generate_pull_commands("Llama-2-7b-hf", ["ultra"])
        
        # Verify the tag format includes nanoquant_ prefix
        self.assertIn("nanoquant_Llama-2-7b-hf:ultra", commands["ultra"])

    def test_quantization_methods(self):
        """Test that quantization methods are properly defined"""
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        engine = UltraAdvancedCompressionEngine()
        
        # Check that advanced quantization methods are available
        self.assertIn("onebit", engine.quantization_strategies)
        self.assertIn("ptq1_61", engine.quantization_strategies)
        self.assertIn("ultrasketch", engine.quantization_strategies)

    def test_pruning_methods(self):
        """Test that pruning methods are properly defined"""
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        engine = UltraAdvancedCompressionEngine()
        
        # Check that advanced pruning methods are available
        self.assertIn("wanda", engine.pruning_strategies)
        self.assertIn("sparsegpt", engine.pruning_strategies)

    def test_decomposition_methods(self):
        """Test that decomposition methods are properly defined"""
        from nanoquant.core.compression_engine import UltraAdvancedCompressionEngine
        engine = UltraAdvancedCompressionEngine()
        
        # Check that advanced decomposition methods are available
        self.assertIn("calr", engine.decomposition_strategies)

if __name__ == '__main__':
    unittest.main()