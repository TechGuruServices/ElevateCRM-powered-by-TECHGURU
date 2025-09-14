#!/usr/bin/env python3
"""Test JWT import"""

try:
    import jwt
    print(f"✓ JWT imported successfully. Version: {jwt.__version__}")
    
    # Test encode/decode
    payload = {"test": "data"}
    secret = "test-secret"
    token = jwt.encode(payload, secret, algorithm="HS256")
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    print(f"✓ JWT encode/decode test passed: {decoded}")
    
except ImportError as e:
    print(f"✗ JWT import failed: {e}")
    
try:
    import jose
    print(f"✓ Jose imported successfully")
except ImportError as e:
    print(f"✗ Jose import failed: {e}")
