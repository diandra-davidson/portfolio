# AI Coding Assistant - Quick Reference Guide

## What Is This?

An AI coding assistant that maintains context about your portfolio website project. It tracks your changes, remembers your project vision, and helps you pick up where you left off.

## How It Works

### 1. **Repository Memory** (Persistent)
Located in `/memories/repo/`:
- `project-vision.md` - Project goals, architecture, features
- `development-log.md` - Commit history, work patterns, TODOs
- `codebase-structure.md` - Directory layout, key files, integrations

The AI reads these files to understand your project context.

### 2. **Change Tracking**
Uses `tools/track_changes.py` to monitor:
- Git commit history
- Modified files
- Branch status
- Development patterns

### 3. **Continuous Learning**
As you work, the AI:
- Observes your coding patterns
- Updates memory files with new insights
- Tracks technical decisions
- Maintains TODO lists

## Common Questions to Ask

### When Starting Work

```
"Where did I leave off in this project?"
"What should I work on next?"
"Summarize my recent commits"
"What's the current status of the project?"
```

### During Development

```
"How should I implement [feature]?"
"What's the architecture for [component]?"
"Where is [functionality] in the codebase?"
"Help me debug [issue]"
"What's the best practice for [task]?"
```

### When Committing

```
"What changes have I made?"
"Review my uncommitted changes"
"Suggest a commit message"
"Should I split this into multiple commits?"
```

### Planning Ahead

```
"What features are incomplete?"
"What's on the roadmap?"
"What technical debt should I address?"
"What are the next milestones?"
```

## Next Session Checklist

1. Run `python tools/track_changes.py summary`
2. Review `git status --short`
3. Write summary for the user on where their work last left off.
5. Commit or park any completed changes before switching tasks.

## Best Practices

### ✅ Do This

1. **Start each session with a summary:**
   ```bash
   python tools/track_changes.py summary
   ```
   Then ask: "Where did I leave off?"

2. **Provide context when asking questions:**
   ```
   "I'm working on the OAuth integration. How should I handle token refresh?"
   ```
   vs. just "How do I refresh tokens?"

3. **Let AI update memory files:**
   After major changes, AI will update the development log

4. **Commit regularly:**
   Helps AI track your progress better

5. **Use descriptive commit messages:**
   AI learns from your naming patterns (e.g., "KAN-8: Setup Docker/Nginx")

### ❌ Avoid This

1. Don't manually edit memory files unless necessary
2. Don't skip commit messages - they're valuable context
3. Don't work in isolation - engage with AI throughout development
4. Don't assume AI knows recent changes - run tracking script first

## Workflow Examples

### Example 1: Starting a New Feature

```bash
# You:
python tools/track_changes.py status

# Then ask AI:
"I want to implement the contact form feature. What should I do first?"

## Next Session Checklist

1. Run `python tools/track_changes.py summary`
2. Review `git status --short`
3. Continue OAuth callback and GitHub metadata work in `main.py`
4. Verify the OAuth result page template exists and renders
5. Commit or park any completed changes before switching tasks

# AI will:
1. Review project-vision.md for requirements
2. Check codebase-structure.md for architecture
3. Suggest implementation steps
4. Reference similar patterns in existing code
```

### Example 2: Debugging an Issue

```
# You:
"The OAuth callback is failing. The error says 'Invalid state parameter'."

# AI will:
1. Review main.py OAuth implementation
2. Check session management
3. Analyze state token flow
4. Suggest fixes with context from your codebase
```

### Example 3: Returning After Time Away

```bash
# You:
python tools/track_changes.py summary

# Then ask AI:
"I haven't worked on this in a few weeks. Can you catch me up?"

# AI will:
1. Review recent commits from development log
2. Check for uncommitted changes
3. Summarize current project status
4. List next planned features from TODO
5. Suggest where to continue
```

## Integration with Development Tools

### Git Integration

The AI tracks:
- Commit messages and patterns
- Branch naming conventions
- Pull request workflow
- Merge strategies

### Docker/Infrastructure

The AI knows:
- Docker Compose configuration
- NGINX setup
- Deployment architecture
- Environment variables

### Code Architecture

The AI understands:
- Flask Blueprint structure
- Template hierarchy
- Static asset organization
- OAuth flow

## Maintenance

### Weekly

- Review development log for accuracy
- Check TODO list progress
- Update project vision if goals change

### Monthly

- Archive old development log entries
- Review and update codebase structure doc
- Assess technical debt

### As Needed

- Update memory files if major architecture changes
- Add new patterns or conventions to notes
- Document new integrations or dependencies

## Advanced Usage

### Asking for Analysis

```
"Analyze my coding patterns from recent commits"
"What areas of the codebase need attention?"
"Are there any code quality issues?"
"Suggest refactoring opportunities"
```

### Strategic Planning

```
"What's the critical path to launch?"
"What dependencies should I update first?"
"How should I prioritize the TODO list?"
"What are the risks in the current architecture?"
```

### Learning from Context

```
"Explain how the OAuth flow works in this codebase"
"What design patterns am I using?"
"How does the deployment process work?"
"Show me examples of how I've implemented [feature]"
```

## Troubleshooting

### AI doesn't remember recent changes

**Solution:** Run `python tools/track_changes.py summary` first

### AI suggests outdated approaches

**Solution:** Check if development-log.md needs updating

### AI isn't aware of new files/features

**Solution:** Commit changes so they appear in git history

### Memory files are out of date

**Solution:** Ask AI to update them:
```
"Can you update the development log with recent progress?"
```

## Tips for Maximum Effectiveness

1. **Be specific in questions** - Include file names, function names, or specific errors

2. **Provide error messages** - Copy-paste full error output for better debugging

3. **Share your thought process** - Tell AI what you're trying to accomplish and why

4. **Ask for explanations** - Understanding context helps with future questions

5. **Use AI for planning** - Before coding, ask AI to help design the approach

6. **Review AI suggestions** - AI provides good starting points, but you know your project best

7. **Update context regularly** - Keep memory files accurate for best results

## Getting Help

When AI doesn't have the answer:
1. Check if relevant context is in memory files
2. Run tracking script to update status
3. Provide more specific details
4. Ask AI to research the topic
5. Request documentation references

Remember: The more you engage with the AI assistant and keep memory files updated, the better it becomes at helping you! 🚀
