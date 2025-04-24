#!/usr/bin/env python3
"""
Script to view unmasked secrets for development/debugging purposes.
WARNING: Do not use this in production as it will display sensitive keys.
"""
import sys
import os
import argparse

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config_secrets import get_config, get_secret, list_config_keys

def main():
    parser = argparse.ArgumentParser(description="View actual contents of config/secret values")
    parser.add_argument("--key", help="Specific key to view")
    parser.add_argument("--all", action="store_true", help="List all keys and values")
    args = parser.parse_args()
    
    print("⚠️  WARNING: This tool displays sensitive information for debugging only ⚠️\n")
    
    if args.key:
        # Get the value for a specific key
        value = get_secret(args.key) or get_config(args.key)
        if value:
            print(f"{args.key} = {value}")
        else:
            print(f"No value found for '{args.key}'")
    
    elif args.all:
        # List all keys with their actual values
        key_values = list_config_keys(mask_sensitive=False)
        if not key_values:
            print("No configuration values found")
            return
            
        print("--- Configuration Values (including secrets) ---")
        for key, value in key_values:
            print(f"{key} = {value}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
