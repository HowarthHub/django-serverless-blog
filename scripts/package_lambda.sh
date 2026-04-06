#!/bin/bash
set -e

echo "Packaging Lambda function..."

BUILD_DIR="$(mktemp -d)"
ZIP_FILE="$(cd infra && pwd)/lambda.zip"

# Copy Django project files
cp -r core blog manage.py requirements.txt "$BUILD_DIR/"

# Install dependencies with Linux ARM64 binaries
# In CI (Linux): pip installs native packages directly
# Locally (macOS): Docker builds Linux-compatible packages
if [ "$(uname)" = "Linux" ]; then
  pip install -r requirements.txt -t "$BUILD_DIR" \
    --platform manylinux2014_aarch64 \
    --only-binary=:all: --quiet
else
  docker run --rm -v "$BUILD_DIR":/out -w /out python:3.12-slim \
    pip install -r requirements.txt -t /out --quiet
fi

# Remove unnecessary files to keep the zip small
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.pyc" -delete 2>/dev/null || true
rm -f "$BUILD_DIR/requirements.txt"

# Create zip
cd "$BUILD_DIR"
rm -f "$ZIP_FILE"
zip -r "$ZIP_FILE" . --quiet

# Cleanup
rm -rf "$BUILD_DIR"

echo "Lambda package created: $ZIP_FILE ($(du -h "$ZIP_FILE" | cut -f1))"
