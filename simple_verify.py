#!/usr/bin/env python3
"""Simple verification"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    import main
    app = main.app

    # Check routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(f"{list(route.methods)[0]} {route.path}")

    latest_routes = [r for r in routes if '/procurement/latest' in r]
    print("Latest routes found:", latest_routes)

    # Check OpenAPI
    openapi_schema = app.openapi()
    procurement_paths = [k for k in openapi_schema.get('paths', {}).keys() if 'procurement' in k]
    print("All procurement paths in OpenAPI:", procurement_paths)

    if '/procurement/latest' in procurement_paths:
        print("SUCCESS: /procurement/latest is in OpenAPI")
    else:
        print("ERROR: /procurement/latest NOT in OpenAPI")

except Exception as e:
    print(f"ERROR: {e}")