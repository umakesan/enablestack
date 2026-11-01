#!/usr/bin/env bash
# Preflight: are the owner skills this conductor delegates to installed?
# Usage: preflight.sh [--ui] [--versions]
#   --ui        also require Impeccable (UI work)
#   --versions  print name=version lines only (used by sdlc_state.py)
# Exit 0 when every required owner is found, 1 otherwise (install commands printed).
# SDLC_PREFLIGHT_HIDE="pstack grill-me" simulates missing owners (validation only).
set -u

ui=0; versions_only=0
for arg in "$@"; do
  case "$arg" in
    --ui) ui=1 ;;
    --versions) versions_only=1 ;;
    *) echo "usage: preflight.sh [--ui] [--versions]" >&2; exit 2 ;;
  esac
done

C="$HOME/.claude"; X="${CODEX_HOME:-$HOME/.codex}"
hidden() { case " ${SDLC_PREFLIGHT_HIDE:-} " in *" $1 "*) return 0 ;; esac; return 1; }

first() { for p in "$@"; do [ -e "$p" ] && { echo "$p"; return 0; }; done; return 1; }

find_owner() {
  hidden "$1" && return 1
  case "$1" in
    brainstorming) first "$C"/plugins/cache/*/superpowers/*/skills/brainstorming/SKILL.md "$C/skills/brainstorming/SKILL.md" "$X/skills/brainstorming/SKILL.md" ;;
    grill-me) first "$C/skills/grill-me/SKILL.md" "$X/skills/grill-me/SKILL.md" "$C"/plugins/cache/*/*/*/skills/grill-me/SKILL.md ;;
    pstack) first "$C"/plugins/cache/*/pstack/*/skills/poteto-mode/SKILL.md "$X/skills/poteto-mode/SKILL.md" ;;
    impeccable) first "$C/skills/impeccable/SKILL.md" "$C"/plugins/cache/*/impeccable/*/skills/impeccable/SKILL.md "$X/skills/impeccable/SKILL.md" ;;
    tech-stack-eval) first "$C/skills/tech-stack-eval/SKILL.md" "$X/skills/tech-stack-eval/SKILL.md" ;;
    domain-modeling) first "$C"/plugins/cache/*/mattpocock-skills/*/skills/*/domain-modeling/SKILL.md "$C"/plugins/cache/*/mattpocock-skills/*/skills/domain-modeling/SKILL.md "$C/skills/domain-modeling/SKILL.md" ;;
  esac
}

version_of() {
  local path="$1" v
  v=$(sed -n 's/^version: *//p' "$path" | head -1)
  [ -n "$v" ] && { echo "$v"; return; }
  case "$path" in
    # plugin cache layout: .../<plugin>/<version>/skills/<skill>/SKILL.md
    */plugins/cache/*) echo "$path" | sed -n 's#.*/\([^/]*\)/skills/.*#\1#p' ;;
    # unversioned skill: a content hash still shows drift on resume
    *) echo "sha-$(shasum -a 256 "$path" | cut -c1-8)" ;;
  esac
}

install_hint() {
  case "$1" in
    brainstorming) echo "claude plugin install superpowers@claude-plugins-official   (Codex: copy skills/brainstorming into ~/.codex/skills)" ;;
    grill-me) echo "npx skills add mattpocock/skills --skill grill-me   (or copy grill-me/SKILL.md from github.com/mattpocock/skills into ~/.claude/skills/grill-me)" ;;
    pstack) echo "claude plugin marketplace add michael-denyer/pstack-claude && claude plugin install pstack@pstack-claude" ;;
    impeccable) echo "npx skills add pbakaus/impeccable   (installs into ~/.claude/skills/impeccable)" ;;
  esac
}

required="brainstorming grill-me pstack"
[ "$ui" = 1 ] && required="$required impeccable"

if [ "$versions_only" = 1 ]; then
  for o in brainstorming grill-me pstack impeccable; do
    p=$(find_owner "$o") && echo "$o=$(version_of "$p")"
  done
  exit 0
fi

missing=0
echo "Required owners:"
for o in $required; do
  if p=$(find_owner "$o"); then
    echo "  ok       $o $(version_of "$p")  ($p)"
  else
    echo "  MISSING  $o -> install: $(install_hint "$o")"
    missing=1
  fi
done

echo "Optional (missing ones show as 'not run' or use the named fallback):"
opt() { if command -v "$1" >/dev/null 2>&1; then echo "  ok       $1"; else echo "  absent   $1 - $2"; fi; }
opt lavish-axi "boards fall back to a Markdown file plus one chat question"
opt node "needed for Playwright UAT; install Node.js"
opt npx "needed for Playwright UAT"
opt ffmpeg "narrated walkthrough video skipped"
opt say "narration skipped (macOS only)"
opt gitleaks "secret scan shows 'not run' (blocking gap): brew install gitleaks"
opt osv-scanner "dependency scan falls back to npm audit / pip-audit: brew install osv-scanner"
opt semgrep "static analysis shows 'not run' (blocking gap): brew install semgrep"
for o in tech-stack-eval domain-modeling; do
  if find_owner "$o" >/dev/null; then echo "  ok       $o"; else echo "  absent   $o - S3 uses the built-in rubric in references/stack.md"; fi
done
[ "$ui" = 0 ] && { find_owner impeccable >/dev/null && echo "  ok       impeccable (not required: ui no)" || echo "  absent   impeccable (only needed for UI work)"; }

if [ "$missing" = 1 ]; then
  echo "STOP: install the missing owner(s) above, then re-run. Do not substitute them inline."
  exit 1
fi
echo "Preflight passed."
