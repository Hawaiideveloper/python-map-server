#!/usr/bin/env python3
"""
Automatic Python Documentation Downloader

This script downloads all Python documentation to make your MCP server
the ultimate Python coding companion. It downloads HTML, PDF, and EPUB
formats for all Python versions to give you comprehensive knowledge.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server.tools.documentation_manager import (
    download_python_documentation,
    PYTHON_DOC_VERSIONS
)


def main():
    """Main function to download Python documentation."""
    parser = argparse.ArgumentParser(
        description="Download Python documentation for all versions"
    )
    parser.add_argument(
        "--versions",
        nargs="*",
        help="Specific versions to download (default: all)",
        default=None
    )
    parser.add_argument(
        "--format",
        choices=["html", "pdf", "epub", "text"],
        default="html",
        help="Documentation format to download (default: html)"
    )
    parser.add_argument(
        "--docs-dir",
        default="docs/python_manuals",
        help="Directory to store documentation (default: docs/python_manuals)"
    )
    parser.add_argument(
        "--stable-only",
        action="store_true",
        help="Download only stable and security-fix versions"
    )
    parser.add_argument(
        "--latest-only",
        action="store_true",
        help="Download only the latest versions (3.13, 3.12, 3.11)"
    )
    
    args = parser.parse_args()
    
    # Determine which versions to download
    if args.latest_only:
        versions = ["3.13", "3.12", "3.11"]
    elif args.stable_only:
        versions = [
            v for v, info in PYTHON_DOC_VERSIONS.items()
            if info["status"] in ["stable", "security-fixes"]
        ]
    elif args.versions:
        versions = args.versions
    else:
        versions = None  # Download all
    
    print("🐍 Python Documentation Downloader")
    print("=" * 50)
    
    if versions:
        print(f"📦 Downloading documentation for versions: {', '.join(versions)}")
    else:
        print("📦 Downloading documentation for ALL Python versions")
        
    print(f"📄 Format: {args.format}")
    print(f"📁 Directory: {args.docs_dir}")
    print()
    
    # Download documentation
    print("🚀 Starting download...")
    result = download_python_documentation(
        versions=versions,
        format_type=args.format,
        docs_dir=args.docs_dir
    )
    
    if result["status"] == "success":
        data = result["result"]
        print("✅ Download completed successfully!")
        print(f"📊 Downloaded: {data['downloaded_versions']} versions")
        print(f"❌ Failed: {data['failed_downloads']} versions") 
        print(f"💾 Total size: {data['total_size_mb']:.1f} MB")
        print(f"📋 Index file: {data['index_file']}")
        print()
        
        # Show download details
        print("📋 Download Details:")
        print("-" * 30)
        for detail in data["download_details"]:
            status_icon = "✅" if detail["status"] == "success" else "❌"
            if detail["status"] == "success":
                print(f"{status_icon} Python {detail['version']} ({detail['python_status']}) - {detail['size_mb']:.1f}MB")
            else:
                print(f"{status_icon} Python {detail['version']} - Error: {detail['error']}")
                
        print()
        print("🎉 Your MCP server now has comprehensive Python documentation!")
        print("🏆 Ready to beat Claude in coding contests!")
        
        # Provide usage instructions
        print()
        print("💡 How to use:")
        print("1. Search docs: Use search_python_documentation tool")
        print("2. Compare versions: Use compare_python_versions tool") 
        print("3. Get features: Use get_python_version_features tool")
        
    else:
        print("❌ Download failed!")
        print(f"Error: {result['error']}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
