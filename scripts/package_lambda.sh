#!/bin/bash
set -e

echo "Packaging Lambda function..."

BUILD_DIR="$(mktemp -d)"
ZIP_FILE="$(cd infra && pwd)/lambda.zip"

# Install Python dependencies into build directory
pip3 install -r requirements.txt -t "$BUILD_DIR" --quiet

# Copy Django project files
cp -r core blog manage.py "$BUILD_DIR/"

# Remove unnecessary files to keep the zip small
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.pyc" -delete 2>/dev/null || true

# Create zip
cd "$BUILD_DIR"
rm -f "$ZIP_FILE"
zip -r "$ZIP_FILE" . --quiet

# Cleanup
rm -rf "$BUILD_DIR"

echo "Lambda package created: $ZIP_FILE ($(du -h "$ZIP_FILE" | cut -f1))"
