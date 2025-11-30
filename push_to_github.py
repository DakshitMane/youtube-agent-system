#!/usr/bin/env python3
"""
GitHub Push Helper Script
Automates the process of pushing your project to GitHub
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n📝 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 YouTube Agent System - GitHub Push Helper")
    print("=" * 70)
    
    # Change to project directory
    project_dir = r"c:\AI Agent\youtube_agent_system"
    if not os.path.exists(project_dir):
        print(f"❌ Project directory not found: {project_dir}")
        sys.exit(1)
    
    os.chdir(project_dir)
    print(f"\n📂 Working directory: {os.getcwd()}")
    
    # Check if already a git repo
    if os.path.exists(".git"):
        print("✅ Git repository already initialized")
    else:
        print("⚠️  Git repository not found. Initializing...")
        if not run_command("git init", "Initialize Git repository"):
            sys.exit(1)
    
    # Configure git (optional)
    print("\n" + "=" * 70)
    print("Git Configuration")
    print("=" * 70)
    
    user_name = input("Enter your name (for git commits): ").strip()
    user_email = input("Enter your email (for git commits): ").strip()
    
    if user_name and user_email:
        run_command(f'git config user.name "{user_name}"', "Configure user name")
        run_command(f'git config user.email "{user_email}"', "Configure user email")
    
    # Check git status
    print("\n" + "=" * 70)
    print("Repository Status")
    print("=" * 70)
    run_command("git status", "Check git status")
    
    # Add files
    if not run_command("git add .", "Add all files to staging"):
        sys.exit(1)
    
    # Create commit
    print("\n" + "=" * 70)
    print("Creating Commit")
    print("=" * 70)
    
    commit_msg = input("Enter commit message (default: 'Initial commit'): ").strip()
    if not commit_msg:
        commit_msg = "Initial commit: YouTube Agent System - AI-powered video generator"
    
    if not run_command(f'git commit -m "{commit_msg}"', "Create commit"):
        print("⚠️  Commit may have failed (possibly nothing to commit)")
    
    # Rename branch
    run_command("git branch -M main", "Rename branch to 'main'")
    
    # Set remote
    print("\n" + "=" * 70)
    print("GitHub Remote Configuration")
    print("=" * 70)
    
    remote_url = input("Enter your GitHub repository URL: ").strip()
    if not remote_url:
        print("❌ GitHub URL is required")
        print("\nTo get your URL:")
        print("1. Go to https://github.com/new")
        print("2. Create a new repository named 'youtube-agent-system'")
        print("3. Copy the HTTPS URL")
        sys.exit(1)
    
    # Check if remote already exists
    run_command('git remote remove origin', "Remove existing remote (if any)")
    
    if not run_command(f'git remote add origin {remote_url}', "Add GitHub remote"):
        sys.exit(1)
    
    # Push to GitHub
    print("\n" + "=" * 70)
    print("Pushing to GitHub")
    print("=" * 70)
    
    if run_command("git push -u origin main", "Push to GitHub"):
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Project pushed to GitHub")
        print("=" * 70)
        print(f"\n🎉 Your project is now on GitHub!")
        print(f"Repository URL: {remote_url}")
        print("\nNext steps:")
        print("1. Add a GitHub star ⭐")
        print("2. Enable GitHub Discussions")
        print("3. Create issue templates")
        print("4. Share on social media")
        print("5. Invite collaborators")
    else:
        print("\n❌ Failed to push to GitHub")
        print("\nTroubleshooting:")
        print("1. Check your GitHub URL is correct")
        print("2. Make sure you have internet connection")
        print("3. Verify your GitHub credentials")
        print("4. Check if using SSH vs HTTPS")
        sys.exit(1)

if __name__ == "__main__":
    main()
