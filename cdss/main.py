#!/usr/bin/env python3
"""
Voice2MR API entry point
"""

import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description='Medical AI Assistant API.')
    parser.add_argument('--port', 
                       type=int, 
                       help='The listening port', 
                       default=8000)
    parser.add_argument('--host',
                       type=str,
                       help='The host to bind to',
                       default="0.0.0.0")
    parser.add_argument('--reload',
                       action='store_true',
                       help='Enable auto-reload')
    args = parser.parse_args()

    uvicorn.run("src.app:app", 
                host=args.host,
                port=args.port,
                reload=args.reload)

if __name__ == "__main__":
    main()
