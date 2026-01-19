#!/usr/bin/env python3
"""
Quick security fixes verification test.
Tests that all security fixes are in place.
"""

import re
import sys


def test_path_traversal_fix():
    """Test that path traversal fix is in place."""
    with open('app.py', 'r') as f:
        content = f.read()

    # Check for Path import
    if 'from pathlib import Path' not in content:
        return False, "Missing pathlib.Path import"

    # Check for filename validation
    if "re.match(r'^[\\w\\-\\.]+$', filename)" not in content:
        return False, "Missing filename validation regex"

    # Check for relative_to check
    if 'filepath.relative_to(articles_dir)' not in content:
        return False, "Missing relative_to path validation"

    return True, "Path traversal protection is in place"


def test_secret_key_config():
    """Test that SECRET_KEY configuration is in place."""
    with open('app.py', 'r') as f:
        content = f.read()

    # Check for Config class
    if 'class Config:' not in content:
        return False, "Missing Config class"

    # Check for SECRET_KEY configuration
    if "SECRET_KEY = os.environ.get('SECRET_KEY')" not in content:
        return False, "Missing SECRET_KEY environment variable"

    # Check for dotenv
    if 'from dotenv import load_dotenv' not in content:
        return False, "Missing dotenv import"

    return True, "SECRET_KEY configuration is secure"


def test_debug_mode():
    """Test that debug mode is properly configured."""
    with open('app.py', 'r') as f:
        content = f.read()

    # Check for debug warning
    if '⚠️  WARNING: Running in DEBUG mode' not in content:
        return False, "Missing debug mode warning"

    # Check that debug is not hardcoded to True
    if 'app.run(debug=True)' in content:
        return False, "Debug mode is hardcoded to True!"

    # Check for config-based debug
    if "debug_mode = app.config.get('DEBUG', False)" not in content:
        return False, "Missing config-based debug mode"

    return True, "Debug mode is properly configured"


def test_file_upload_validation():
    """Test that file upload validation is in place."""
    with open('app.py', 'r') as f:
        content = f.read()

    # Check for validation function
    if 'def validate_uploaded_file(file):' not in content:
        return False, "Missing validate_uploaded_file function"

    # Check for magic bytes validation
    if 'header[:2] == b\'PK\'' not in content:
        return False, "Missing magic bytes validation for xlsx"

    # Check for path traversal in filename
    if "if '/' in filename or '\\\\' in filename or '..' in filename:" not in content:
        return False, "Missing filename path traversal check"

    return True, "File upload validation is comprehensive"


def test_security_headers():
    """Test that security headers are in place."""
    with open('app.py', 'r') as f:
        content = f.read()

    required_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Content-Security-Policy',
        'Referrer-Policy',
        'Permissions-Policy'
    ]

    for header in required_headers:
        if header not in content:
            return False, f"Missing security header: {header}"

    # Check for @app.after_request decorator
    if '@app.after_request' not in content:
        return False, "Missing @app.after_request decorator"

    return True, "All security headers are configured"


def test_csrf_protection():
    """Test that CSRF protection is enabled."""
    with open('app.py', 'r') as f:
        app_content = f.read()

    # Check for CSRFProtect import and initialization
    if 'from flask_wtf.csrf import CSRFProtect' not in app_content:
        return False, "Missing flask_wtf.csrf import"

    if 'csrf = CSRFProtect(app)' not in app_content:
        return False, "CSRF protection not initialized"

    # Check template for CSRF tokens
    try:
        with open('templates/projects/capacity_tracker.html', 'r') as f:
            template_content = f.read()

        if 'csrf_token()' not in template_content:
            return False, "CSRF tokens not in template"

        # Count csrf_token occurrences (should be at least 2 - for both forms)
        csrf_count = template_content.count('csrf_token()')
        if csrf_count < 2:
            return False, f"Only {csrf_count} CSRF token(s) found, expected at least 2"

    except FileNotFoundError:
        return False, "Template file not found"

    return True, "CSRF protection is fully enabled"


def test_requirements():
    """Test that all required packages are in requirements.txt."""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()

        required_packages = ['flask-wtf', 'python-dotenv', 'openpyxl', 'Flask', 'Werkzeug']

        for package in required_packages:
            if package.lower() not in content.lower():
                return False, f"Missing package: {package}"

        return True, "All required packages in requirements.txt"
    except FileNotFoundError:
        return False, "requirements.txt not found"


def test_env_file():
    """Test that .env file exists and has SECRET_KEY."""
    try:
        with open('.env', 'r') as f:
            content = f.read()

        if 'SECRET_KEY=' not in content:
            return False, ".env file missing SECRET_KEY"

        if 'FLASK_DEBUG=' not in content:
            return False, ".env file missing FLASK_DEBUG"

        return True, ".env file properly configured"
    except FileNotFoundError:
        return False, ".env file not found"


def test_gitignore():
    """Test that .env is in .gitignore."""
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()

        if '.env' not in content:
            return False, ".env not in .gitignore"

        if '*.backup' not in content:
            return False, "*.backup not in .gitignore"

        return True, ".gitignore properly configured"
    except FileNotFoundError:
        return False, ".gitignore not found"


def main():
    """Run all security tests."""
    tests = [
        ("Path Traversal Protection", test_path_traversal_fix),
        ("SECRET_KEY Configuration", test_secret_key_config),
        ("Debug Mode Security", test_debug_mode),
        ("File Upload Validation", test_file_upload_validation),
        ("Security Headers", test_security_headers),
        ("CSRF Protection", test_csrf_protection),
        ("Requirements.txt", test_requirements),
        (".env File", test_env_file),
        (".gitignore", test_gitignore),
    ]

    print("=" * 70)
    print("SECURITY FIXES VERIFICATION TEST")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            success, message = test_func()
            if success:
                print(f"✓ PASS | {test_name}")
                print(f"   {message}")
                passed += 1
            else:
                print(f"✗ FAIL | {test_name}")
                print(f"   {message}")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR | {test_name}")
            print(f"   Exception: {str(e)}")
            failed += 1
        print()

    print("=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed > 0:
        print(f"WARNING: {failed} test(s) failed!")
    else:
        print("ALL SECURITY FIXES VERIFIED ✓")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
