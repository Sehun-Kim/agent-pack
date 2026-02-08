/**
 * agent-pack reminders plugin for OpenCode.ai
 *
 * OpenCode doesn't have Claude Code-style hooks. This plugin injects a small
 * reminder policy into the system prompt so the agent proactively reminds
 * (and suggests commands) before risky/expensive operations.
 */

const agentPackRemindersPlugin = async () => {
  const reminders = `<IMPORTANT>
Agent-pack reminders (OpenCode, warn-only):

- Before \`git commit\` / \`git push\`: run /preflight (status + diff + tests).
- Before build/test/dev server: use tmux (/tmux-remind).
- Before \`git switch -c\` / \`git checkout -b\`: prefer git worktree (/worktree).

Keep reminders to 1 line. Do not block.
</IMPORTANT>`;

  return {
    'experimental.chat.system.transform': async (_input, output) => {
      if (!output.system) output.system = [];
      output.system.push(reminders);
    }
  };
};

// Backward/forward compatibility across OpenCode plugin loaders.
// - Some versions expect a default export.
// - Some versions import a named plugin export.
export default agentPackRemindersPlugin;
export const AgentPackRemindersPlugin = agentPackRemindersPlugin;
