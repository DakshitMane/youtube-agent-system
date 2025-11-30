#!/bin/env pwsh
# GitHub Push Helper Script for PowerShell
# Run: .\push_to_github.ps1

Write-Host "=" * 70
Write-Host "🚀 YouTube Agent System - GitHub Push Helper" -ForegroundColor Green
Write-Host "=" * 70

$projectDir = "c:\AI Agent\youtube_agent_system"

# Check project directory
if (-not (Test-Path $projectDir)) {
    Write-Host "❌ Project directory not found: $projectDir" -ForegroundColor Red
    exit 1
}

Set-Location $projectDir
Write-Host "`n📂 Working directory: $(Get-Location)" -ForegroundColor Cyan

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "`n⚠️  Git repository not found. Initializing..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "`n✅ Git repository already initialized" -ForegroundColor Green
}

# Configure git
Write-Host "`n" + "=" * 70
Write-Host "Git Configuration" -ForegroundColor Cyan
Write-Host "=" * 70

$userName = Read-Host "Enter your name (for git commits)"
$userEmail = Read-Host "Enter your email (for git commits)"

if ($userName -and $userEmail) {
    git config user.name "$userName"
    git config user.email "$userEmail"
    Write-Host "✅ Git configured" -ForegroundColor Green
}

# Check status
Write-Host "`n" + "=" * 70
Write-Host "Repository Status" -ForegroundColor Cyan
Write-Host "=" * 70
git status

# Add files
Write-Host "`n📝 Adding files to staging..." -ForegroundColor Yellow
git add .
Write-Host "✅ Files added" -ForegroundColor Green

# Create commit
Write-Host "`n" + "=" * 70
Write-Host "Creating Commit" -ForegroundColor Cyan
Write-Host "=" * 70

$commitMsg = Read-Host "Enter commit message (default: 'Initial commit')"
if (-not $commitMsg) {
    $commitMsg = "Initial commit: YouTube Agent System - AI-powered video generator"
}

git commit -m "$commitMsg"
Write-Host "✅ Commit created" -ForegroundColor Green

# Rename branch
Write-Host "`n📝 Renaming branch to 'main'..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ Branch renamed" -ForegroundColor Green

# Set remote
Write-Host "`n" + "=" * 70
Write-Host "GitHub Remote Configuration" -ForegroundColor Cyan
Write-Host "=" * 70

$remoteUrl = Read-Host "Enter your GitHub repository URL"

if (-not $remoteUrl) {
    Write-Host "`n❌ GitHub URL is required" -ForegroundColor Red
    Write-Host "`nTo get your URL:" -ForegroundColor Yellow
    Write-Host "1. Go to https://github.com/new" 
    Write-Host "2. Create a new repository named 'youtube-agent-system'"
    Write-Host "3. Copy the HTTPS URL"
    exit 1
}

# Remove existing remote if it exists
git remote remove origin 2>$null

git remote add origin "$remoteUrl"
Write-Host "✅ Remote configured" -ForegroundColor Green

# Push to GitHub
Write-Host "`n" + "=" * 70
Write-Host "Pushing to GitHub" -ForegroundColor Cyan
Write-Host "=" * 70

Write-Host "`n⏳ Pushing... (this may take a few moments)" -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n" + "=" * 70
    Write-Host "✅ SUCCESS! Project pushed to GitHub" -ForegroundColor Green
    Write-Host "=" * 70
    Write-Host "`n🎉 Your project is now on GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: $remoteUrl" -ForegroundColor Cyan
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Add a GitHub star ⭐"
    Write-Host "2. Enable GitHub Discussions"
    Write-Host "3. Create issue templates"
    Write-Host "4. Share on social media"
    Write-Host "5. Invite collaborators"
} else {
    Write-Host "`n❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check your GitHub URL is correct"
    Write-Host "2. Make sure you have internet connection"
    Write-Host "3. Verify your GitHub credentials"
    Write-Host "4. Check if using SSH vs HTTPS"
    exit 1
}
