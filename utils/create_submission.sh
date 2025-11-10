#!/bin/bash
# Creates a submission zip without including data files and other ignored items

echo "Creating submission package..."
echo ""

# Ask for full name
read -p "Enter your full name (e.g., Anna Andersson): " fullname

# Convert to lowercase and replace spaces with underscores
filename=$(echo "$fullname" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
filename="${filename}.zip"

# Check if git repository has commits
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo ""
    echo "Error: No git commits found. Please commit your changes first!"
    echo ""
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo ""
    echo "Warning: You have uncommitted changes. Please commit them first!"
    echo ""
    exit 1
fi

# Create zip using git to respect .gitignore
# This ensures we only include tracked files and exclude everything in .gitignore
git archive -o "$filename" HEAD --verbose

echo ""
echo "✓ Submission package created: $filename"
echo "This includes all your code and analysis, excluding data files and other ignored items."
echo "Please submit this file."
