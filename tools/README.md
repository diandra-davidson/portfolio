# Portfolio Development Tools

This directory contains helper scripts for tracking development progress and assisting the AI coding agent.

## Scripts

### `track_changes.py`

A development progress tracker that helps the AI assistant maintain context about your work.

**Features:**
- Show current git status and branch info
- Display recent commit history
- List modified and staged files
- Generate comprehensive summaries for AI assistant

**Usage:**

```bash
# Show current status (default)
python tools/track_changes.py
python tools/track_changes.py status

# Generate full summary for AI assistant
python tools/track_changes.py summary

# Show last N commits (default 10)
python tools/track_changes.py commits 20
```

**When to use:**
- At the start of each coding session
- Before committing changes
- When asking AI assistant "where did I leave off?"
- To provide context for complex questions

## AI Assistant Integration

The AI coding assistant uses these tools along with repository memory files to:

1. **Track your progress** - Monitors git commits and file changes
2. **Maintain context** - Remembers your project vision and architecture
3. **Provide continuity** - Helps you pick up where you left off
4. **Suggest next steps** - Based on development log and TODOs

## Repository Memory

The AI assistant maintains these memory files in `/memories/repo/`:

- `project-vision.md` - Project goals, features, architecture overview
- `development-log.md` - Recent commits, work patterns, next TODOs
- `codebase-structure.md` - Directory structure, key files, integrations
- `keyring.md` - Keyring configuration notes

These files are automatically updated by the AI assistant as you work.

## Workflow

### Starting a New Session

1. Run `python tools/track_changes.py summary` to see current state
2. Ask AI assistant: "What did I work on last? Where should I continue?"
3. AI reviews git history and memory files
4. AI provides summary and suggests next tasks

### During Development

- Make changes to your code
- AI assistant tracks modifications
- Commit when ready
- AI updates development log

### Ending a Session

1. Review uncommitted changes
2. Decide what to commit
3. AI updates development log with progress
4. Notes any open TODOs for next session

## Example Questions for AI Assistant

- "Where did I leave off in this project?"
- "What have I been working on recently?"
- "What should I work on next?"
- "Summarize my recent commits"
- "What features are still incomplete?"
- "Show me the project roadmap"
- "What's the current architecture?"

The AI assistant will use these tools and memory files to provide accurate, contextual answers.
