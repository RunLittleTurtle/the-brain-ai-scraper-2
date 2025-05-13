#!/usr/bin/env python
"""
Run script for LangGraph Studio with the intent inference graph.

This script properly configures and starts the LangGraph Studio server
with optimized settings to prevent CORS issues in Chrome.
"""
import os
import sys
import subprocess
import argparse
import json
from intent_inference.utils.visualization import setup_langsmith_tracing

def main():
    """Run LangGraph Studio with proper configuration."""
    parser = argparse.ArgumentParser(description="Run LangGraph Studio with intent inference graph")
    parser.add_argument("--port", type=int, default=2024, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Setup LangSmith tracing
    setup_langsmith_tracing()
    
    # Add CORS-compatible config to langgraph.json
    langgraph_json_path = "langgraph.json"
    with open(langgraph_json_path, "r") as f:
        config = json.load(f)
    
    # Ensure config has optimal settings for Chrome/local network access
    if "config" not in config:
        config["config"] = {}
    
    config["config"].update({
        "app_address": f"localhost:{args.port}",
        "host": args.host,
        "port": args.port,
        "cors": {
            "allow_origins": ["*"],
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "allow_credentials": True
        },
        "tracing": {
            "langsmith": True
        }
    })
    
    # Write updated config back to file
    with open(langgraph_json_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Starting LangGraph Studio server on {args.host}:{args.port}")
    print("Access the Studio UI at:")
    print(f"https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:{args.port}")
    print("\nPress Ctrl+C to stop the server.")
    
    # Build the langgraph command with options for LangGraph 0.4.3
    cmd = [
        "langgraph", "dev", 
        "--port", str(args.port),
        "--host", args.host
    ]
    
    if args.debug:
        cmd.append("--debug")
    
    # Run the command in a subprocess
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping LangGraph Studio server...")
        sys.exit(0)

if __name__ == "__main__":
    main()
