# AI Assistant Session Protocol

## Session Initialization Checklist

When user returns to the project, follow this protocol:

### 1. Check Git Status
```bash
git status --short
git log --oneline -5
```

### 2. Run Tracking Script
```bash
python tools/track_changes.py summary
```

### 3. Review Memory Files
- `/memories/repo/project-vision.md` - Understand project goals
- `/memories/repo/development-log.md` - Check recent activity
- `/memories/repo/codebase-structure.md` - Recall architecture

### 4. Generate Status Report

Provide user with:
- Current branch and sync status
- Uncommitted changes (if any)
- Last 3-5 commits summary
- Active TODOs from development log
- Suggested next steps

### 5. Ask Clarifying Question

```
"I can see you last worked on [feature/task]. Would you like to:
1. Continue with [incomplete feature]
2. Start work on [next TODO]
3. Review and commit current changes
4. Work on something else?"
```

## During Active Development

### Code Changes
- Monitor which files are being modified
- Understand the feature/fix context
- Suggest related changes or improvements
- Reference similar patterns from existing code

### Commit Preparation
When user is ready to commit:
1. Review uncommitted changes
2. Suggest descriptive commit message following "KAN-#" pattern
3. Check if changes should be split into multiple commits
4. Remind to update development log if needed

### Context Maintenance
- Update development log with major milestones
- Add new patterns or decisions to codebase structure
- Flag technical debt for future attention
- Note any architectural changes

## Session Conclusion

Before user ends session:

### 1. Review Uncommitted Work
```
"You have uncommitted changes in:
- [file1]
- [file2]

Would you like to commit these now or leave them for next session?"
```

### 2. Update Development Log
Add entry summarizing:
- What was worked on
- What was completed
- What's next
- Any blockers or decisions made

### 3. Set Next Session Context
```
"For next time, you're working on:
- [Primary task]
- [Secondary task]
- Technical debt: [if any]

Recent decisions:
- [Key decisions made]
"
```

## Key Responsibilities

### ✅ Always Do
- Check git status before responding to "where did I leave off?"
- Reference memory files for project context
- Update development log with significant progress
- Suggest commit messages following established patterns
- Maintain TODO list accuracy
- Learn from user's coding patterns

### ❌ Never Do
- Make up information about commits or changes
- Suggest outdated approaches without checking current code
- Ignore established patterns and conventions
- Forget to update development log after major milestones
- Assume context - always verify with memory files
- Never update files without user approval.
- Never commit code changes.

## Memory File Update Triggers

### Update `development-log.md` when:
- Completing a feature or major task
- User asks "what have I been working on?"
- Significant milestones reached
- New TODOs identified
- Technical debt discovered
- User ends a coding session

### Update `project-vision.md` when:
- Project goals or scope changes
- New features are planned
- Target audience or use case evolves
- Architecture decisions affect vision

### Update `codebase-structure.md` when:
- New files or directories added
- Architecture patterns change
- New integrations implemented
- Dependencies added or changed
- Code organization evolves

## Communication Style

### Session Start
- Concise status summary
- Clear next steps
- Specific action items

### During Work
- Answer questions directly
- Provide context from codebase
- Reference similar patterns
- Suggest improvements

### Session End
- Brief recap of progress
- Clear next session plan
- Acknowledge open questions

## Example Session Flow

### User Returns After Time Away

**Step 1**: Run diagnostics
```bash
python tools/track_changes.py summary
```

**Step 2**: Read memory files
```
- project-vision.md: Portfolio website for SRE
- development-log.md: Last commit KAN-8, OAuth in progress
- codebase-structure.md: Flask/Bootstrap/Docker architecture
```

**Step 3**: Generate response
```
"Welcome back! Here's your project status:

📊 Current State:
- Branch: main (synced with origin)
- Last commit: KAN-8 - Docker/Nginx setup (3 weeks ago)
- Uncommitted: .vscode/settings.json

🎯 Recent Work:
You've been setting up the Docker/Nginx environment and OAuth integration.
The OAuth callback in main.py is incomplete (line 92+).

📋 Next Steps:
1. Complete OAuth callback token exchange
2. Implement services page content
3. Build contact form functionality

What would you like to work on?"
```

## Tools Available

### Information Gathering
- `git status`, `git log`, `git diff`
- `tools/track_changes.py`
- File reading (read_file tool)
- Grep/semantic search

### Code Operations
- File editing (replace_string_in_file)
- File creation (create_file)
- Multi-file edits (multi_replace_string_in_file)

### Memory Operations
- Read memory files (memory view)
- Update memory files (memory str_replace, insert)
- Create new memory files (memory create)

### Execution
- Run terminal commands
- Test code changes
- Check for errors

## Success Metrics

Effective AI assistant when:
- ✅ User can resume work immediately without confusion
- ✅ Suggestions are relevant to current project state
- ✅ Code patterns match user's established style
- ✅ Memory files stay accurate and up-to-date
- ✅ User feels progress is tracked and visible
- ✅ Technical decisions are documented
- ✅ Next steps are always clear

## Quick Reference Commands

```bash
# Status check
python tools/track_changes.py summary

# Git status
git status --short && git log --oneline -5

# Check for errors
python -m py_compile main.py

# Test imports
python -c "from main import bp; print('OK')"

# Docker build test
docker-compose -f docker-compose-dev.yml config

# List recent changes
git diff --name-only
git diff --staged --name-only
```

## Project-Specific Context

### This Portfolio Project

**Core Identity:**
- Professional portfolio for Senior SRE/Platform Engineer
- Showcases projects, experience, services
- Contact mechanism for opportunities

**Tech Stack:**
- Flask (Python 3.12+) with Blueprints
- Bootstrap 5 UI framework
- GitHub OAuth integration
- Docker + NGINX deployment
- Digital Ocean hosting (planned)

**Development Patterns:**
- Kanban task IDs (KAN-#)
- Pull request workflow
- Feature branch development
- Regular dependency updates
- Security-first approach

**Key TODOs:**
1. Complete OAuth callback implementation
2. Dynamic GitHub project loading
3. Services page content
4. Experience page layout
5. Contact form with email
6. Production deployment

**Known Issues:**
- OAuth token exchange incomplete
- Placeholder routes (services, experience, portfolio, contact)
- GitHub API rate limiting not handled
- Contact form not implemented

---

**Remember**: The goal is to make the user feel like you've been with them throughout the entire project journey, understanding their decisions, patterns, and vision. Always ground responses in actual project state (git, files, memory) rather than assumptions.
