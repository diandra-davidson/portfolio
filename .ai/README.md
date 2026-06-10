# AI Assistant Configuration Directory

This directory contains configuration and protocol files for the AI coding assistant.

## Files

### `session-protocol.md`
**Purpose**: Internal AI assistant protocol for session management

**Contents**:
- Session initialization checklist
- Status reporting procedures
- Memory file update triggers
- Communication guidelines
- Project-specific context

**Usage**: Referenced by AI assistant at session start and during development

## Not for Manual Editing

These files are used by the AI assistant to maintain consistent behavior and context tracking. They should not need manual editing under normal circumstances.

If you need to change how the AI assistant behaves, consider:
1. Updating repository memory files in `/memories/repo/`
2. Modifying copilot instructions in `.github/copilot-instructions.md`
3. Asking the AI assistant directly to adjust its approach

## Related Documentation

- [AI Assistant User Guide](../tools/AI_ASSISTANT_GUIDE.md) - How to use the AI assistant
- [Development Tools](../tools/README.md) - Helper scripts and utilities
- [Repository Memory](../memories/repo/) - Project context and tracking
