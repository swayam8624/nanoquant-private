#!/bin/bash

echo "Starting cleanup of markdown and test files..."

# Count files before cleanup
echo "Counting files before cleanup..."
MD_COUNT=$(find . -name "*.md" -not -name "README.md" -not -path "./.git/*" | wc -l)
TEST_COUNT=$(find . -name "*test*.py" -not -path "./.git/*" | wc -l)

echo "Found $MD_COUNT markdown files (excluding README.md)"
echo "Found $TEST_COUNT test files"

# Delete markdown files except README.md
echo "Deleting markdown files..."
find . -name "*.md" -not -name "README.md" -not -path "./.git/*" -delete

# Delete test files
echo "Deleting test files..."
find . -name "*test*.py" -not -path "./.git/*" -delete

# Count remaining files
echo "Counting files after cleanup..."
REMAINING_MD=$(find . -name "*.md" -not -path "./.git/*" | wc -l)

echo "Cleanup complete!"
echo "Remaining markdown files: $REMAINING_MD (should be README.md files only)"
echo "Test files deleted: $TEST_COUNT"