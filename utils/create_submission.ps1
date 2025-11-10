# PowerShell script for Windows users
# Creates a submission zip without including data files and other ignored items

Write-Host "Creating submission package..." -ForegroundColor Cyan
Write-Host ""

# Ask for full name
$fullname = Read-Host "Enter your full name (e.g., Anna Andersson)"

# Convert to lowercase and replace spaces with underscores
$filename = $fullname.ToLower() -replace ' ', '_'
$filename = "$filename.zip"

# Check if git repository has commits
git rev-parse HEAD 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: No git commits found. Please commit your changes first!" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Check for uncommitted changes
git diff-index --quiet HEAD -- 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Warning: You have uncommitted changes. Please commit them first:" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Use git archive to respect .gitignore
# This ensures we only include tracked files and exclude everything in .gitignore
git archive -o $filename HEAD

Write-Host ""
Write-Host "Submission package created: $filename" -ForegroundColor Green
Write-Host "This includes all your code and analysis, excluding data files and other ignored items." -ForegroundColor Cyan
Write-Host "Please submit this file." -ForegroundColor Yellow
