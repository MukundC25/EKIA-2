#!/usr/bin/env bash
# Start (or restart) the Cloudflare quick tunnel to the local backend and point Vercel at it.
# Quick-tunnel URLs change on every start, so this rewrites frontend/vercel.json, commits and pushes;
# Vercel redeploys automatically from GitHub.
# Usage: deploy/refresh_tunnel.sh          (backend must be running: docker compose up -d)
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"; cd "$ROOT"
LOG="data/tunnel.log"

curl -sf http://localhost:8001/health >/dev/null || { echo "Backend not running on :8001 — run: docker compose up -d"; exit 1; }

pkill -f "cloudflared tunnel --no-autoupdate --url" 2>/dev/null || true
nohup cloudflared tunnel --no-autoupdate --url http://localhost:8001 > "$LOG" 2>&1 &
disown

URL=""
for _ in $(seq 1 30); do
  URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | head -1 || true)"
  [ -n "$URL" ] && break
  sleep 1
done
[ -n "$URL" ] || { echo "Tunnel did not start; see $LOG"; exit 1; }
echo "Tunnel: $URL"

sed -i '' -E "s#https://[a-z0-9-]+\.trycloudflare\.com#$URL#g" frontend/vercel.json
if git diff --quiet frontend/vercel.json; then
  echo "vercel.json already points at this tunnel."
else
  git add frontend/vercel.json
  git commit -m "chore: point Vercel API rewrites at $URL"
  git push
  echo "Pushed — Vercel will redeploy in about a minute."
fi
