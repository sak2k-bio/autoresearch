"""
Test runner for AutoResearch Bio-Medical Pipeline
"""
import os
import sys
import traceback

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables first
try:
    from utils.env_loader import load_env_with_dotenv, load_env_variables
    load_env_with_dotenv()
    load_env_variables()
except ImportError:
    print("utils.env_loader not found, attempting manual .env loading...")
    # Manual .env loading as fallback
    import pathlib
    from pathlib import Path
    
    # Look for .env files and load them
    current_dir = Path.cwd()
    for _ in range(4):
        for env_file in ['.env.local', '.env', '.env.example']:
            env_path = current_dir / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Remove quotes if present
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]
                                
                                # Only set if not already set to avoid overriding system vars
                                if key not in os.environ:
                                    os.environ[key] = value
                except Exception as e:
                    print(f"Warning: Could not load {env_path}: {e}")
        
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent

def test_environment():
    """Test that environment variables are properly set"""
    print("Testing environment variables...")
    
    required_vars = ['TAVILY_API_KEY']
    optional_vars = ['GEMINI_API_KEY_1', 'GEMINI_API_KEY_2', 'GEMINI_API_KEY_3', 'GEMINI_API_KEY_4', 'GEMINI_API_KEY_5', 'GEMINI_MODEL']
    
    missing_required = []
    found_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if os.getenv(var):
            found_optional.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("Please set these variables before running the pipeline.")
        print("\nCheck that your .env file contains:")
        for var in required_vars:
            print(f"  {var}=your_actual_key_here")
        return False
    else:
        print("✅ All required environment variables are set")
        print(f"   - TAVILY_API_KEY: {'Set' if os.getenv('TAVILY_API_KEY') else 'Not set'}")
    
    if found_optional:
        print(f"✅ Found optional environment variables: {found_optional}")
    else:
        print("⚠️  No optional environment variables found (this is okay for testing)")
    
    print(f"✅ GEMINI_MODEL is set to: {os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')}")
    
    return True

def test_config():
    """Test that configuration loads properly"""
    print("\nTesting configuration...")
    
    try:
        from bio_research.config import config
        print(f"✅ Configuration loaded successfully")
        print(f"   - Tavily API key: {'Set' if config.tavily_api_key else 'Not set'}")
        print(f"   - Gemini API keys: {len(config.gemini_api_keys)} keys loaded")
        print(f"   - Gemini model: {config.gemini_model}")
        print(f"   - Min paper score: {config.MIN_PAPER_SCORE}")
        print(f"   - Min curiosity score: {config.MIN_CURIOSITY_SCORE}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed to load: {e}")
        traceback.print_exc()
        return False

def test_modules():
    """Test that all modules can be imported"""
    print("\nTesting module imports...")
    
    modules_to_test = [
        'bio_research.keyword_generator',
        'bio_research.paper_finder', 
        'bio_research.paper_scoring',
        'bio_research.insight_extractor',
        'bio_research.mechanism_simplifier',
        'bio_research.hook_generator',
        'bio_research.post_generator',
        'bio_research.optimizer',
        'bio_research.topic_memory',
        'bio_research.learning_loop'
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {failed_imports}")
        return False
    else:
        print("\n✅ All modules imported successfully")
        return True

def test_single_iteration():
    """Test running a single iteration of the pipeline"""
    print("\nTesting single pipeline iteration...")
    
    try:
        from autoresearch_bio import AutoResearchBio
        autoresearch_bio = AutoResearchBio()
        
        print("✅ AutoResearchBio instance created successfully")
        
        # Run a single iteration
        print("Running single pipeline iteration...")
        autoresearch_bio.run_pipeline()
        
        print("✅ Single iteration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Single iteration failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("AutoResearch Bio-Medical Pipeline - Test Runner")
    print("="*60)
    
    all_tests_passed = True
    
    # Test environment
    if not test_environment():
        all_tests_passed = False
    
    # Test configuration
    if not test_config():
        all_tests_passed = False
    
    # Test module imports
    if not test_modules():
        all_tests_passed = False
    
    # Test single iteration (only if environment is properly configured)
    if os.getenv('TAVILY_API_KEY'):
        if not test_single_iteration():
            all_tests_passed = False
    else:
        print("\n⚠️  Skipping single iteration test (TAVILY_API_KEY not set)")
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 All tests passed! The AutoResearch Bio-Medical Pipeline is ready to run.")
        print("\nTo start the autonomous system:")
        print("  python autoresearch_bio.py")
        print("\nTo run a single iteration for testing:")
        print("  python autoresearch_bio.py --run-once")
        print("\nTo print the learning summary:")
        print("  python autoresearch_bio.py --print-learning")
    else:
        print("❌ Some tests failed. Please fix the issues before running the pipeline.")
    print("="*60)

if __name__ == "__main__":
    main()
