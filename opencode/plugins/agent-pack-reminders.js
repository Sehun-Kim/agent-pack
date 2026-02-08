/**
 * agent-pack reminders plugin for OpenCode.ai
 *
 * OpenCode doesn't have Claude Code-style hooks. This plugin injects a small
 * reminder policy into the system prompt so the agent proactively reminds
 * (and suggests commands) before risky/expensive operations.
 */

export const AgentPackRemindersPlugin = async () => {
  const reminders = `<IMPORTANT>
Agent-pack reminders (OpenCode, warn-only):

- Before \\`git commit\\` / \\`git push\\`: run /preflight (status + diff + tests).
- Before build/test/dev server: use tmux (/tmux-remind).
- Before \\`git switch -c\\` / \\`git checkout -b\\`: prefer git worktree (/worktree).

Keep reminders to 1 line. Do not block.
</IMPORTANT>`;

  return {
    'experimental.chat.system.transform': async (_input, output) => {
      (output.system ||= []).push(reminders);
    }
  };
};
