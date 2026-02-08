#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TS="$(date +%Y%m%d%H%M%S)"

SUPERPOWERS_REPO="https://github.com/obra/superpowers.git"
SUPERPOWERS_COMMIT="469a6d81ebb8b827e284d4afb090c6c622d97747"  # v4.1.1
SUPERPOWERS_PLUGIN_SHA256="900783cc631112007ffef521f7ffc51a1db3ac6fbac57c5b054d41120285c040"
SUPERPOWERS_BOOTSTRAP_SKILL_SHA256="81d921b16502091f44e8669bbcfae74b87bbf4295d03fff70a98e81d73af60a6"

backup_then_link () {
  local src="$1"
  local dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" || -L "$dst" ]]; then
    mv "$dst" "${dst}.bak.${TS}"
  fi
  ln -s "$src" "$dst"
  echo "linked: $dst -> $src"
}

sha256_file () {
  local path="$1"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$path" | awk '{print $1}'
    return 0
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$path" | awk '{print $1}'
    return 0
  fi
  python3 - <<PY
import hashlib
from pathlib import Path

p = Path("$path")
h = hashlib.sha256(p.read_bytes()).hexdigest()
print(h)
PY
}

install_external_skills_global () {
  local config_dir="$HOME/.config/opencode"
  local dest_dir="$config_dir/skills"
  local sources="$ROOT/skill-sources/global.sources.json"
  local lock="$ROOT/skill-sources/global.lock.json"

  if ! command -v python3 >/dev/null 2>&1; then
    echo "external-skills: python3 not found; skipping"
    return 0
  fi
  if [[ ! -f "$lock" ]]; then
    echo "external-skills: lock not found at $lock; skipping"
    return 0
  fi

  mkdir -p "$dest_dir"

  echo "external-skills: installing globally from $lock ..."
  python3 "$ROOT/scripts/skills_install.py" \
    --project-sources "$sources" \
    --project-lock "$lock" \
    --dest "$dest_dir" \
    || {
      echo "external-skills: install failed; skipping"
      return 0
    }
}

install_superpowers_opencode () {
  local config_dir="$HOME/.config/opencode"
  local sp_dir="$config_dir/superpowers"
  local plugin_src="$sp_dir/.opencode/plugins/superpowers.js"
  local plugin_dst="$config_dir/plugins/superpowers.js"
  local skills_dst="$config_dir/skills/superpowers"
  local skills_src="$sp_dir/skills"
  local bootstrap_skill_src="$skills_src/using-superpowers/SKILL.md"

  if ! command -v git >/dev/null 2>&1; then
    echo "superpowers: git not found; skipping"
    return 0
  fi

  mkdir -p "$config_dir/plugins" "$config_dir/skills"

  if [[ ! -d "$sp_dir/.git" ]]; then
    if [[ -e "$sp_dir" && ! -d "$sp_dir" ]]; then
      echo "superpowers: $sp_dir exists but is not a directory; skipping"
      return 0
    fi
    if [[ ! -d "$sp_dir" ]]; then
      echo "superpowers: cloning into $sp_dir..."
      git clone --no-checkout "$SUPERPOWERS_REPO" "$sp_dir" || {
        echo "superpowers: clone failed; skipping"
        return 0
      }
    else
      echo "superpowers: $sp_dir exists but is not a git repo; skipping"
      return 0
    fi
  fi

  echo "superpowers: pinning to $SUPERPOWERS_COMMIT..."
  git -C "$sp_dir" fetch --depth 1 origin "$SUPERPOWERS_COMMIT" || {
    echo "superpowers: fetch failed; skipping"
    return 0
  }
  git -C "$sp_dir" checkout --detach "$SUPERPOWERS_COMMIT" || {
    echo "superpowers: checkout failed; skipping"
    return 0
  }

  local head
  head="$(git -C "$sp_dir" rev-parse HEAD)"
  if [[ "$head" != "$SUPERPOWERS_COMMIT" ]]; then
    echo "superpowers: HEAD mismatch ($head != $SUPERPOWERS_COMMIT); skipping"
    return 0
  fi

  if [[ ! -f "$plugin_src" ]]; then
    echo "superpowers: plugin not found at $plugin_src; skipping"
    return 0
  fi
  if [[ ! -f "$bootstrap_skill_src" ]]; then
    echo "superpowers: bootstrap skill not found at $bootstrap_skill_src; skipping"
    return 0
  fi

  local plugin_sha
  plugin_sha="$(sha256_file "$plugin_src")"
  if [[ "$plugin_sha" != "$SUPERPOWERS_PLUGIN_SHA256" ]]; then
    echo "superpowers: plugin sha256 mismatch; skipping"
    echo "superpowers: expected $SUPERPOWERS_PLUGIN_SHA256"
    echo "superpowers: got      $plugin_sha"
    return 0
  fi

  local bootstrap_sha
  bootstrap_sha="$(sha256_file "$bootstrap_skill_src")"
  if [[ "$bootstrap_sha" != "$SUPERPOWERS_BOOTSTRAP_SKILL_SHA256" ]]; then
    echo "superpowers: bootstrap skill sha256 mismatch; skipping"
    echo "superpowers: expected $SUPERPOWERS_BOOTSTRAP_SKILL_SHA256"
    echo "superpowers: got      $bootstrap_sha"
    return 0
  fi

  backup_then_link "$plugin_src" "$plugin_dst"
  backup_then_link "$skills_src" "$skills_dst"
  echo "superpowers: installed (plugin + skills)"
}

install_agent_pack_opencode_plugins () {
  local config_dir="$HOME/.config/opencode"
  mkdir -p "$config_dir/plugins"
  backup_then_link "$ROOT/opencode/plugins/agent-pack-reminders.js" "$config_dir/plugins/agent-pack-reminders.js"
}

echo "== Installing agent-pack from: $ROOT =="

# 1) OpenCode global config
mkdir -p "$HOME/.config/opencode"
backup_then_link "$ROOT/opencode/opencode.jsonc" "$HOME/.config/opencode/opencode.json"

# 1-2) oh-my-opencode global config
backup_then_link "$ROOT/opencode/oh-my-opencode.jsonc" "$HOME/.config/opencode/oh-my-opencode.json"

# 1-2-2) OpenCode commands (e.g., /tokenscope)
# NOTE: This will replace any existing command directory (it is backed up).
backup_then_link "$ROOT/opencode/command" "$HOME/.config/opencode/command"

# 1-2-3) OpenCode local plugins (agent-pack)
install_agent_pack_opencode_plugins

# 1-3) External skill sources (metadata only)
# - Source of truth lives in this repo
# - Projects may override with their own `.opencode/skill-sources.json` (see docs)
backup_then_link "$ROOT/skill-sources" "$HOME/.config/opencode/skill-sources"

# 1-3-1) External skills (global, pinned + hashed)
# - Uses skill-sources/global.lock.json
# - Installs into ~/.config/opencode/skills/
install_external_skills_global

# 1-4) Superpowers (OpenCode plugin + skills)
# - Pinned to a commit and verified by sha256 for bootstrap components.
install_superpowers_opencode

# 2) Create/refresh a single OpenCode rules entrypoint (AGENTS.md)
#    Keep it as a regular file to make debugging easy.
bash "$ROOT/scripts/refresh-agents.sh"

# 3) Claude-compatible locations (for future migration and shared structure)
mkdir -p "$HOME/.claude"
backup_then_link "$ROOT/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
backup_then_link "$ROOT/claude/rules"     "$HOME/.claude/rules"
backup_then_link "$ROOT/claude/skills"    "$HOME/.claude/skills"

# Claude Code commands + hooks presets
backup_then_link "$ROOT/claude/commands"  "$HOME/.claude/commands"
backup_then_link "$ROOT/claude/hooks"     "$HOME/.claude/hooks"

# Claude Code settings bootstrap (warn-only hooks)
# - If settings.json does not exist, create it with our hooks enabled.
# - If it exists, do NOT overwrite; print merge guidance.
CLAUDE_SETTINGS_FILE="$HOME/.claude/settings.json"
if [[ ! -e "$CLAUDE_SETTINGS_FILE" && ! -L "$CLAUDE_SETTINGS_FILE" ]]; then
  cp "$ROOT/claude/hooks/hooks.json" "$CLAUDE_SETTINGS_FILE"
  echo "claude: created $CLAUDE_SETTINGS_FILE (warn-only hooks enabled)"
else
  echo "claude: settings.json exists; not modifying. To enable agent-pack hooks, merge:"
  echo "  $HOME/.claude/hooks/hooks.json  ->  $HOME/.claude/settings.json"
fi

# Local cache for external skills (contents are NOT committed to agent-pack)
mkdir -p "$HOME/.claude/skills-external"

# 4) TokenScope vendor tokenizer deps
#
# TokenScope's tokenizer loader expects vendored deps at:
#   ~/.config/opencode/plugin/vendor/node_modules/{js-tiktoken,@huggingface/transformers}
#
# Depending on how the plugin was installed, deps may already exist at:
#   ~/.config/opencode/plugin/node_modules
#
# To make this work across machines (and avoid duplicate installs), we:
# - Create vendor/
# - Symlink vendor/node_modules -> ../node_modules when possible
# - Fallback to npm install into vendor/ when node_modules is absent

TOKENSCOPE_PLUGIN_DIR="$HOME/.config/opencode/plugin"
TOKENSCOPE_LIB_DIR="$TOKENSCOPE_PLUGIN_DIR/tokenscope-lib"
TOKENSCOPE_VENDOR_DIR="$TOKENSCOPE_PLUGIN_DIR/vendor"
TOKENSCOPE_VENDOR_NODE_MODULES="$TOKENSCOPE_VENDOR_DIR/node_modules"

# Make vendor deps available even on first-time machines.
# (OpenCode may install the TokenScope plugin on first run, but the tokenizer loader
# expects this vendor path to already exist.)
mkdir -p "$TOKENSCOPE_VENDOR_DIR"

# Prefer reusing existing plugin-level node_modules if present and vendor/node_modules not already set.
if [[ ! -e "$TOKENSCOPE_VENDOR_NODE_MODULES" && -d "$TOKENSCOPE_PLUGIN_DIR/node_modules" ]]; then
  # Create a relative symlink so it remains portable if $HOME changes.
  ln -s "../node_modules" "$TOKENSCOPE_VENDOR_NODE_MODULES"
  echo "tokenscope: linked $TOKENSCOPE_VENDOR_NODE_MODULES -> ../node_modules"
fi

# If required packages are missing under vendor, install them into vendor.
TOKENSCOPE_TIKTOKEN_PKG="$TOKENSCOPE_VENDOR_NODE_MODULES/js-tiktoken/package.json"
TOKENSCOPE_TRANSFORMERS_PKG="$TOKENSCOPE_VENDOR_NODE_MODULES/@huggingface/transformers/package.json"

if [[ ! -f "$TOKENSCOPE_TIKTOKEN_PKG" || ! -f "$TOKENSCOPE_TRANSFORMERS_PKG" ]]; then
  if command -v npm >/dev/null 2>&1; then
    echo "tokenscope: ensuring vendor tokenizers (may take 1-2 minutes)..."
    # Pin versions that match the TokenScope installer script defaults.
    npm install --prefix "$TOKENSCOPE_VENDOR_DIR" js-tiktoken@1.0.15 @huggingface/transformers@3.1.2 --save-exact
  else
    echo "tokenscope: npm not found; cannot install vendor tokenizers automatically"
    echo "tokenscope: install Node.js/npm, then re-run: $ROOT/scripts/install.sh"
  fi
fi

echo "== Done =="
