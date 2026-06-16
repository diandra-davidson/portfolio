#!/usr/bin/env python3
"""
Track Changes - Development Progress Tracker

This script helps track changes in the codebase and generates summaries
for the AI coding assistant to maintain context.

Usage:
    python tools/track_changes.py status        # Show current status
    python tools/track_changes.py summary       # Generate work summary
    python tools/track_changes.py commits [N]   # Show last N commits
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


def get_git_status():
    """Get current git status."""
    return run_command("git status --short")


def get_recent_commits(count=10):
    """Get recent commit history."""
    cmd = f'git log --oneline -n {count} --pretty=format:"%h|%s|%ar|%an"'
    output = run_command(cmd)
    if not output or output.startswith("Error"):
        return []
    
    commits = []
    for line in output.split('\n'):
        if '|' in line:
            hash_val, msg, time, author = line.split('|', 3)
            commits.append({
                'hash': hash_val,
                'message': msg,
                'time': time,
                'author': author
            })
    return commits


def get_changed_files():
    """Get list of modified files."""
    output = run_command("git diff --name-only")
    staged = run_command("git diff --staged --name-only")
    
    modified = output.split('\n') if output else []
    staged_files = staged.split('\n') if staged else []
    
    return {
        'modified': [f for f in modified if f],
        'staged': [f for f in staged_files if f]
    }


def get_branch_info():
    """Get current branch and tracking info."""
    branch = run_command("git branch --show-current")
    tracking = run_command("git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo 'No upstream'")
    ahead_behind = run_command("git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo '0\t0'")
    
    try:
        ahead, behind = ahead_behind.split()
    except:
        ahead, behind = "0", "0"
    
    return {
        'branch': branch,
        'upstream': tracking,
        'ahead': int(ahead),
        'behind': int(behind)
    }


def show_status():
    """Show current development status."""
    print("=" * 60)
    print("📊 PORTFOLIO PROJECT - CURRENT STATUS")
    print("=" * 60)
    print()
    
    # Branch info
    branch_info = get_branch_info()
    print(f"🌿 Branch: {branch_info['branch']}")
    print(f"   Upstream: {branch_info['upstream']}")
    if branch_info['ahead'] > 0:
        print(f"   ⬆️  {branch_info['ahead']} commit(s) ahead")
    if branch_info['behind'] > 0:
        print(f"   ⬇️  {branch_info['behind']} commit(s) behind")
    print()
    
    # Changed files
    changes = get_changed_files()
    if changes['modified'] or changes['staged']:
        print("📝 Modified Files:")
        for f in changes['staged']:
            print(f"   ✅ {f} (staged)")
        for f in changes['modified']:
            print(f"   📄 {f}")
        print()
    else:
        print("✨ Working directory clean\n")
    
    # Recent commits
    print("📜 Recent Commits:")
    commits = get_recent_commits(5)
    for commit in commits:
        print(f"   {commit['hash']} - {commit['message']}")
        print(f"      {commit['time']} by {commit['author']}")
    print()


def show_commits(count=10):
    """Show detailed commit history."""
    print("=" * 60)
    print(f"📜 LAST {count} COMMITS")
    print("=" * 60)
    print()
    
    commits = get_recent_commits(count)
    for i, commit in enumerate(commits, 1):
        print(f"{i}. {commit['hash']} - {commit['message']}")
        print(f"   Author: {commit['author']}")
        print(f"   Time: {commit['time']}")
        print()


def generate_summary():
    """Generate a comprehensive summary for the AI assistant."""
    print("=" * 60)
    print("🤖 AI ASSISTANT SESSION SUMMARY")
    print("=" * 60)
    print()
    
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Branch and status
    branch_info = get_branch_info()
    print("## Current State")
    print(f"- Branch: {branch_info['branch']}")
    print(f"- Upstream: {branch_info['upstream']}")
    print(f"- Status: {branch_info['ahead']} ahead, {branch_info['behind']} behind")
    print()
    
    # Changes
    changes = get_changed_files()
    if changes['modified'] or changes['staged']:
        print("## Uncommitted Changes")
        if changes['staged']:
            print("Staged:")
            for f in changes['staged']:
                print(f"  - {f}")
        if changes['modified']:
            print("Modified:")
            for f in changes['modified']:
                print(f"  - {f}")
        print()
    
    # Recent work
    print("## Recent Commits (Last 10)")
    commits = get_recent_commits(10)
    for commit in commits:
        print(f"- {commit['hash']}: {commit['message']} ({commit['time']})")
    print()
    
    print("## Next Steps")
    print("Review the changes above and decide on:")
    print("1. Whether to commit current changes")
    print("2. What feature/fix to work on next")
    print("3. Any technical debt to address")
    print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    elif command == "summary":
        generate_summary()
    elif command == "commits":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_commits(count)
    else:
        print("Unknown command. Usage:")
        print("  python tools/track_changes.py status")
        print("  python tools/track_changes.py summary")
        print("  python tools/track_changes.py commits [N]")
        sys.exit(1)


if __name__ == "__main__":
    main()
