#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

HOOK_DIR="$REPO_ROOT/.githooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [[ ! -d "$HOOK_DIR" ]]; then
  echo "ERROR: Hook directory not found: $HOOK_DIR" >&2
  exit 1
fi

if [[ ! -d "$GIT_HOOKS_DIR" ]]; then
  echo "ERROR: Git hooks directory not found: $GIT_HOOKS_DIR" >&2
  exit 1
fi

cp "$HOOK_DIR/pre-push" "$GIT_HOOKS_DIR/pre-push"
chmod +x "$GIT_HOOKS_DIR/pre-push"

echo "Installed pre-push hook to $GIT_HOOKS_DIR/pre-push"

git config core.hooksPath "$HOOK_DIR"
echo "Configured repository git hooks path to $HOOK_DIR"
