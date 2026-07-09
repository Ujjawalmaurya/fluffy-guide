#!/usr/bin/env python
"""
Utility script to generate the openapi.json file for the FastAPI application.
Run this script from the backend directory to refresh Swagger documentation.
"""
import os
import sys
import json

# Ensure backend directory is in python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.main import app

def generate_spec():
    print("Generating OpenAPI specification...")
    openapi = app.openapi()
    
    # Force server URL default
    openapi['servers'] = [{'url': 'http://localhost:8000'}]
    
    # Save to backend/docs/openapi.json
    backend_docs_path = os.path.join(backend_dir, 'docs', 'openapi.json')
    with open(backend_docs_path, 'w') as f:
        json.dump(openapi, f, indent=2)
    print(f"Saved to: {backend_docs_path}")
    
    # Save to root docs/openapi.json
    root_docs_path = os.path.join(os.path.dirname(backend_dir), 'docs', 'openapi.json')
    if os.path.isdir(os.path.dirname(root_docs_path)):
        with open(root_docs_path, 'w') as f:
            json.dump(openapi, f, indent=2)
        print(f"Saved to: {root_docs_path}")

if __name__ == '__main__':
    generate_spec()
