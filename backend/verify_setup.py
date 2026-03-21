#!/usr/bin/env python
"""
🔍 PIXEL PIRATES - GENERATION SETUP VERIFICATION

Checks all prerequisites before running content generation:
- Python version
- Required packages
- Environment variables (API keys)
- MongoDB connectivity
- File structure
- Storage directories
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header():
    print(f"\n{Colors.BLUE}{'='*80}")
    print("🔍 PIXEL PIRATES - SETUP VERIFICATION")
    print(f"{'='*80}{Colors.END}\n")

def check_python_version():
    """Check Python version >= 3.8"""
    print(f"{Colors.BLUE}[1] Python Version{Colors.END}")
    version = sys.version_info
    if version >= (3, 8):
        print(f"  {Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro}{Colors.END}")
        return True
    else:
        print(f"  {Colors.RED}❌ Python 3.8+ required (found {version.major}.{version.minor}){Colors.END}")
        return False

def check_packages():
    """Check required Python packages"""
    print(f"\n{Colors.BLUE}[2] Required Packages{Colors.END}")
    
    required = {
        'fastapi': 'FastAPI',
        'motor': 'Motor (Async MongoDB)',
        'google.generativeai': 'Google Generative AI',
        'httpx': 'HTTPX (Async HTTP)',
        'reportlab': 'ReportLab (PDF)',
        'pymongo': 'PyMongo',
        'dotenv': 'Python-dotenv',
    }
    
    missing = []
    
    for package, name in required.items():
        try:
            __import__(package)
            print(f"  {Colors.GREEN}✅ {name}{Colors.END}")
        except ImportError:
            print(f"  {Colors.RED}❌ {name} (missing){Colors.END}")
            missing.append(package)
    
    if missing:
        print(f"\n  {Colors.YELLOW}Install missing packages:{Colors.END}")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def check_env_vars():
    """Check required environment variables"""
    print(f"\n{Colors.BLUE}[3] Environment Variables{Colors.END}")
    
    checks = {
        'GEMINI_API_KEY': 'Gemini API Key',
        'MONGODB_URL': 'MongoDB URL (optional, defaults to localhost)',
        'MONGODB_DATABASE': 'MongoDB Database Name (optional, defaults to pixel_pirates)',
    }
    
    results = {}
    for var_name, description in checks.items():
        value = os.getenv(var_name)
        if var_name == 'MONGODB_URL':
            value = value or 'mongodb://localhost:27017/'
            print(f"  {Colors.GREEN}✅ {description}: {value}{Colors.END}")
            results[var_name] = True
        elif var_name == 'MONGODB_DATABASE':
            value = value or 'pixel_pirates'
            print(f"  {Colors.GREEN}✅ {description}: {value}{Colors.END}")
            results[var_name] = True
        else:
            if value:
                masked = value[:20] + '...' if len(value) > 20 else value
                print(f"  {Colors.GREEN}✅ {description}: {masked}{Colors.END}")
                results[var_name] = True
            else:
                print(f"  {Colors.RED}❌ {description}: NOT SET{Colors.END}")
                results[var_name] = False
    
    # Also check YouTube API key (hardcoded)
    youtube_key = "IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc"
    print(f"  {Colors.GREEN}✅ YouTube API Key: {youtube_key[:20]}...{Colors.END}")
    results['YOUTUBE_API_KEY'] = True
    
    if not results.get('GEMINI_API_KEY'):
        print(f"\n  {Colors.YELLOW}To get GEMINI_API_KEY:{Colors.END}")
        print(f"  1. Go to https://makersuite.google.com/app/apikey")
        print(f"  2. Copy your API key")
        print(f"  3. Add to .env: GEMINI_API_KEY=your_key_here")
        return False
    
    return all(results.get(k) for k in ['GEMINI_API_KEY', 'YOUTUBE_API_KEY'])

def check_mongodb():
    """Check MongoDB connectivity"""
    print(f"\n{Colors.BLUE}[4] MongoDB Connection{Colors.END}")
    
    try:
        from pymongo import MongoClient
        mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db_name = os.getenv('MONGODB_DATABASE', 'pixel_pirates')
        db = client[db_name]
        
        print(f"  {Colors.GREEN}✅ Connected to MongoDB{Colors.END}")
        print(f"     URL: {mongo_url}")
        print(f"     Database: {db_name}")
        
        # Check existing content
        topics_col = db['topics']
        topic_count = topics_col.count_documents({})
        print(f"     Topics in DB: {topic_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"  {Colors.RED}❌ MongoDB connection failed: {e}{Colors.END}")
        print(f"\n  {Colors.YELLOW}Make sure MongoDB is running:{Colors.END}")
        print(f"  - Local: mongod")
        print(f"  - Cloud: Update MONGODB_URL to your Atlas connection string")
        return False

def check_file_structure():
    """Check required files exist"""
    print(f"\n{Colors.BLUE}[5] File Structure{Colors.END}")
    
    required_files = {
        'verify_and_generate_topics.py': 'Topics generation script',
        'generate_complete_content.py': 'Content generation script',
        'generate_all_content.py': 'Master orchestration script',
        'app/routes/content_delivery.py': 'Content delivery API routes',
        'app/models/__init__.py': 'Data models',
    }
    
    backend_dir = Path(__file__).parent
    all_exist = True
    
    for filename, description in required_files.items():
        filepath = backend_dir / filename
        if filepath.exists():
            print(f"  {Colors.GREEN}✅ {description}{Colors.END}")
        else:
            print(f"  {Colors.RED}❌ {description} (missing){Colors.END}")
            all_exist = False
    
    return all_exist

def check_storage_dirs():
    """Check and create storage directories"""
    print(f"\n{Colors.BLUE}[6] Storage Directories{Colors.END}")
    
    backend_dir = Path(__file__).parent
    storage_dir = backend_dir / 'storage' / 'pdfs'
    
    try:
        storage_dir.mkdir(parents=True, exist_ok=True)
        print(f"  {Colors.GREEN}✅ PDF storage ready: {storage_dir}{Colors.END}")
        return True
    except Exception as e:
        print(f"  {Colors.RED}❌ Cannot create storage dir: {e}{Colors.END}")
        return False

def check_api_keys_validity():
    """Quick sanity check on API keys"""
    print(f"\n{Colors.BLUE}[7] API Keys Format Check{Colors.END}")
    
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    youtube_key = "IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc"
    
    # Gemini keys are typically long alphanumeric
    if gemini_key and len(gemini_key) > 20 and gemini_key.isalnum():
        print(f"  {Colors.GREEN}✅ GEMINI_API_KEY format looks valid{Colors.END}")
        gemini_ok = True
    else:
        print(f"  {Colors.RED}❌ GEMINI_API_KEY format invalid (too short or wrong chars){Colors.END}")
        gemini_ok = False
    
    # YouTube key should be long and contain specific pattern
    if youtube_key and len(youtube_key) > 30:
        print(f"  {Colors.GREEN}✅ YouTube API Key format looks valid{Colors.END}")
        youtube_ok = True
    else:
        print(f"  {Colors.RED}❌ YouTube API Key format invalid{Colors.END}")
        youtube_ok = False
    
    return gemini_ok and youtube_ok

def print_summary(checks: dict):
    """Print summary of all checks"""
    print(f"\n{Colors.BLUE}{'='*80}")
    print("✅ VERIFICATION SUMMARY")
    print(f"{'='*80}{Colors.END}\n")
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        icon = f"{Colors.GREEN}✅{Colors.END}" if passed else f"{Colors.RED}❌{Colors.END}"
        status = "PASS" if passed else "FAIL"
        print(f"{icon} {check_name:<40} {Colors.GREEN if passed else Colors.RED}{status}{Colors.END}")
    
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    
    if all_passed:
        print(f"{Colors.GREEN}✅ ALL CHECKS PASSED - Ready to generate content!{Colors.END}\n")
        print(f"{Colors.BLUE}Next Steps:{Colors.END}")
        print(f"1. Run: python generate_all_content.py")
        print(f"2. This will generate content for all 200 topics")
        print(f"3. Estimated time: 30-60 minutes")
        print(f"4. Then start the backend: python main.py\n")
        return True
    else:
        print(f"{Colors.RED}❌ Some checks failed - Please fix issues above{Colors.END}\n")
        print(f"{Colors.YELLOW}Troubleshooting Guide:{Colors.END}")
        print(f"1. Python issue: Update Python to 3.8+")
        print(f"2. Package issue: pip install [package_name]")
        print(f"3. Env vars: Add to .env file and reload")
        print(f"4. MongoDB: Start with 'mongod' or use MongoDB Atlas")
        print(f"5. File structure: Verify files exist in backend directory\n")
        return False

def main():
    """Run all checks"""
    print_header()
    
    checks = {
        'Python Version': check_python_version(),
        'Required Packages': check_packages(),
        'Environment Variables': check_env_vars(),
        'MongoDB Connection': check_mongodb(),
        'File Structure': check_file_structure(),
        'Storage Directories': check_storage_dirs(),
        'API Keys Format': check_api_keys_validity(),
    }
    
    success = print_summary(checks)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
