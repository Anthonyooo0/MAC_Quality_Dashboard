#!/usr/bin/env python
"""
Standalone sync script - Called by Streamlit to avoid threading issues
This runs in a separate process, so it won't conflict with Streamlit's event loop
"""

import sys
import json
from main import process

if __name__ == "__main__":
    try:
        # Run the sync process
        result = process()
        
        # Output result as JSON
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)