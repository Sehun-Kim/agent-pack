#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  git-worktree.sh new <branch> [base]
  git-worktree.sh list
  git-worktree.sh path <branch>
  git-worktree.sh remove <branch> [--force]

Notes:
- Worktrees are created under:
    <repo-parent>/.worktrees/<repo-name>/<branch>
  (Fallback: $HOME/.worktrees/<repo-name>/<branch> if parent isn't writable)
- 'new' creates a new branch if it doesn't exist; otherwise attaches the existing branch.
- 'remove' is destructive and requires --force.
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 2
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || die "not inside a git repo"
}

worktrees_base_dir() {
  local root parent repo base
  root="$(repo_root)"
  parent="$(dirname "$root")"
  repo="$(basename "$root")"
  base="$parent/.worktrees/$repo"
  if mkdir -p "$base" 2>/dev/null; then
    echo "$base"
    return 0
  fi
  base="$HOME/.worktrees/$repo"
  mkdir -p "$base" || die "cannot create worktree base dir: $base"
  echo "$base"
}

worktree_path_for_branch() {
  local branch base
  branch="$1"
  base="$(worktrees_base_dir)"
  echo "$base/$branch"
}

cmd_new() {
  local branch base path
  branch="$1"
  base="${2:-HEAD}"
  path="$(worktree_path_for_branch "$branch")"

  if [[ -e "$path" ]]; then
    die "path already exists: $path"
  fi

  if git show-ref --verify --quiet "refs/heads/$branch"; then
    git worktree add "$path" "$branch"
  else
    git worktree add -b "$branch" "$path" "$base"
  fi

  echo "OK: created worktree"
  echo "  branch: $branch"
  echo "  path:   $path"
  echo
  echo "Suggested (tmux):"
  echo "  tmux new -s wt-$branch"
  echo "  cd \"$path\""
}

cmd_list() {
  git worktree list
}

cmd_path() {
  local branch path
  branch="$1"
  path="$(git worktree list --porcelain | awk -v b="refs/heads/$branch" '
    $1=="worktree"{p=$2}
    $1=="branch" && $2==b{print p; exit 0}
  ' || true)"
  if [[ -z "$path" ]]; then
    # Fallback to the conventional path.
    path="$(worktree_path_for_branch "$branch")"
  fi
  echo "$path"
}

cmd_remove() {
  local branch force path
  branch="$1"
  force="${2:-}"
  [[ "$force" == "--force" ]] || die "remove requires --force"

  path="$(cmd_path "$branch")"
  [[ -e "$path" ]] || die "worktree path not found: $path"

  git worktree remove "$path"
  echo "OK: removed worktree at $path"
}

main() {
  need_cmd git
  need_cmd awk

  local cmd
  cmd="${1:-}"
  case "$cmd" in
    new)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      cmd_new "$2" "${3:-}"
      ;;
    list)
      cmd_list
      ;;
    path)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      cmd_path "$2"
      ;;
    remove|rm)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      cmd_remove "$2" "${3:-}"
      ;;
    -h|--help|help|"")
      usage
      ;;
    *)
      usage
      exit 2
      ;;
  esac
}

main "$@"
