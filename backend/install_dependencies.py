#!/usr/bin/env python3
"""
Rice Mill Management System - Dependency Installation Script
Handles Python 3.13 compatibility issues and installs dependencies safely
"""

import subprocess
import sys
import platform
import pkg_resources
from pathlib import Path

def get_python_version():
    """Get current Python version"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def check_python_compatibility():
    """Check if current Python version is supported"""
    major, minor = sys.version_info.major, sys.version_info.minor
    
    if major != 3:
        print(f"❌ Error: Python {major}.{minor} is not supported. Please use Python 3.8 or higher.")
        return False
    
    if minor < 8:
        print(f"❌ Error: Python 3.{minor} is not supported. Please use Python 3.8 or higher.")
        return False
    
    if minor >= 13:
        print(f"⚠️  Warning: Python 3.{minor} detected. Some AI packages may not be available.")
        print("   Using Python 3.13 compatible requirements...")
        return "py313"
    
    print(f"✅ Python {major}.{minor} is supported.")
    return True

def install_package(package_name, fallback=None):
    """Install a package with fallback option"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        if fallback:
            print(f"Failed to install {package_name}, trying fallback: {fallback}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", fallback])
                print(f"Successfully installed {fallback}")
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to install both {package_name} and {fallback}")
                return False
        else:
            print(f"Failed to install {package_name}")
            return False

def install_requirements_file(requirements_file):
    """Install requirements from file"""
    try:
        print(f"📋 Installing requirements from {requirements_file}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print(f"✅ Successfully installed requirements from {requirements_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements from {requirements_file}")
        print(f"Error: {e}")
        return False

def install_core_dependencies():
    """Install core dependencies that are essential for the system"""
    core_packages = [
        "Flask==3.0.3",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-JWT-Extended==4.6.0",
        "Flask-CORS==4.0.0",
        "numpy>=1.26.0",
        "pandas>=2.0.0",
        "requests>=2.30.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.0.0",
        "pydantic>=2.0.0"
    ]
    
    print("🔧 Installing core dependencies...")
    failed_packages = []
    
    for package in core_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"⚠️  Some core packages failed to install: {failed_packages}")
        return False
    
    print("✅ All core dependencies installed successfully!")
    return True

def install_ai_dependencies():
    """Install AI dependencies with fallbacks for Python 3.13"""
    ai_packages = [
        ("torch>=2.0.0", None),
        ("transformers>=4.30.0", None),
        ("scikit-learn>=1.5.0", None),
        ("google-generativeai>=0.7.0", None),
        ("openai>=1.0.0", None),
        ("langchain>=0.1.0", None),
        ("faiss-cpu>=1.7.0", None)
    ]
    
    print("🤖 Installing AI dependencies...")
    failed_packages = []
    
    for package, fallback in ai_packages:
        if not install_package(package, fallback):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"⚠️  Some AI packages failed to install: {failed_packages}")
        print("   The system will work with basic functionality.")
    else:
        print("✅ All AI dependencies installed successfully!")
    
    return len(failed_packages) == 0

def install_optional_dependencies():
    """Install optional dependencies for enhanced features"""
    optional_packages = [
        ("opencv-python>=4.8.0", "opencv-python-headless>=4.8.0"),
        ("scikit-image>=0.21.0", None),
        ("matplotlib>=3.7.0", None),
        ("seaborn>=0.12.0", None),
        ("plotly>=5.17.0", None)
    ]
    
    print("🎨 Installing optional dependencies...")
    
    for package, fallback in optional_packages:
        install_package(package, fallback)
    
    print("✅ Optional dependencies installation completed!")

def verify_installation():
    """Verify that key packages are installed and working"""
    print("🔍 Verifying installation...")
    
    critical_packages = [
        "flask",
        "sqlalchemy", 
        "numpy",
        "pandas",
        "requests"
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} is working")
        except ImportError:
            print(f"❌ {package} is not available")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing critical packages: {missing_packages}")
        return False
    
    print("✅ All critical packages are working!")
    return True

def create_fallback_config():
    """Create configuration for systems with missing AI dependencies"""
    config_content = """
# Fallback configuration for systems with limited AI dependencies
AI_FEATURES_ENABLED = False
COMPUTER_VISION_ENABLED = False
VOICE_RECOGNITION_ENABLED = False
ADVANCED_ANALYTICS_ENABLED = False

# Basic features that should always work
BASIC_CRUD_ENABLED = True
REPORTING_ENABLED = True
AUTHENTICATION_ENABLED = True
"""
    
    config_path = Path("config/fallback_config.py")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"📝 Created fallback configuration at {config_path}")

def main():
    """Main installation function"""
    print("Rice Mill Management System - Dependency Installation")
    print("=" * 60)
    
    # Check Python compatibility
    python_check = check_python_compatibility()
    if python_check is False:
        sys.exit(1)
    
    # Upgrade pip first
    print("Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("pip upgraded successfully")
    except subprocess.CalledProcessError:
        print("Failed to upgrade pip, continuing anyway...")
    
    # Choose requirements file based on Python version
    if python_check == "py313":
        requirements_file = "requirements-py313.txt"
        print(f"📋 Using Python 3.13 compatible requirements: {requirements_file}")
    else:
        requirements_file = "requirements.txt"
        print(f"📋 Using standard requirements: {requirements_file}")
    
    # Try to install from requirements file first
    if Path(requirements_file).exists():
        if install_requirements_file(requirements_file):
            print("✅ Requirements installed successfully!")
        else:
            print("⚠️  Requirements file installation failed, trying individual packages...")
            
            # Install core dependencies
            if not install_core_dependencies():
                print("❌ Failed to install core dependencies. Exiting.")
                sys.exit(1)
            
            # Try AI dependencies
            install_ai_dependencies()
            
            # Install optional dependencies
            install_optional_dependencies()
    else:
        print(f"❌ Requirements file {requirements_file} not found!")
        print("📦 Installing core dependencies individually...")
        
        if not install_core_dependencies():
            print("❌ Failed to install core dependencies. Exiting.")
            sys.exit(1)
        
        install_ai_dependencies()
        install_optional_dependencies()
    
    # Verify installation
    if verify_installation():
        print("\n🎉 Installation completed successfully!")
        print("Rice Mill Management System is ready to run!")
    else:
        print("\nInstallation completed with some issues.")
        print("Creating fallback configuration...")
        create_fallback_config()
        print("System will run with basic functionality.")
    
    print("\nNext steps:")
    print("1. Set up your environment variables in .env file")
    print("2. Initialize the database: python -c 'from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()'")
    print("3. Run the application: python app.py")

if __name__ == "__main__":
    main()
