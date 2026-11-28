#!/usr/bin/env bash
# Start (or restart) the Cloudflare quick tunnel to the local backend and point Vercel at it.
# Quick-tunnel URLs change on every start, so this regenerates frontend/vercel.json, commits and pushes;
# Vercel redeploys automatically from GitHub.
# Usage: deploy/refresh_tunnel.sh          (backend must be running: docker compose up -d)
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"; cd "$ROOT"
LOG="data/tunnel.log"
URL_RE='^https://[a-z0-9-]+\.trycloudflare\.com$'

curl -sf http://localhost:8001/health >/dev/null || { echo "Backend not running on :8001 — run: docker compose up -d"; exit 1; }

pkill -f "cloudflared tunnel --no-autoupdate --url" 2>/dev/null || true
sleep 1
nohup cloudflared tunnel --no-autoupdate --url http://localhost:8001 > "$LOG" 2>&1 &
disown

# -a: the log can contain non-text bytes; without it grep prints "Binary file ... matches"
URL=""
for _ in $(seq 1 30); do
  URL="$(grep -aoE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | grep -v '^https://api\.' | head -1 || true)"
  [[ "$URL" =~ $URL_RE ]] && break
  URL=""
  sleep 1
done
[ -n "$URL" ] || { echo "Tunnel did not start; see $LOG"; exit 1; }
echo "Tunnel: $URL"

# Only repoint Vercel once the tunnel really reaches the backend.
# Resolve the new hostname via public DNS (1.1.1.1): the Mac's resolver often caches the
# "not found" answer from a lookup made before the record existed, which would fail this check
# even though the tunnel is reachable from the internet (and from Vercel).
HOST="${URL#https://}"
tunnel_ok() {
  local ip
  ip="$(dig +short "$HOST" @1.1.1.1 2>/dev/null | grep -E '^[0-9.]+$' | head -1 || true)"
  if [ -n "$ip" ]; then
    curl -sf -m 10 --resolve "$HOST:443:$ip" "$URL/health" >/dev/null
  else
    curl -sf -m 10 "$URL/health" >/dev/null
  fi
}
ok=""
for _ in $(seq 1 30); do
  if tunnel_ok; then ok=1; break; fi
  sleep 2
done
[ -n "$ok" ] || { echo "Tunnel is up but not reaching the backend yet; vercel.json left unchanged. See $LOG"; exit 1; }
echo "Tunnel verified: reaches the backend."

cat > frontend/vercel.json <<JSON
{
  "\$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    { "source": "/api/graph/", "destination": "$URL/api/graph/" },
    { "source": "/api/:path*", "destination": "$URL/api/:path*" },
    { "source": "/health", "destination": "$URL/health" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
JSON

if git diff --quiet frontend/vercel.json; then
  echo "vercel.json already points at this tunnel."
else
  git add frontend/vercel.json
  git commit -m "chore: point Vercel API rewrites at $URL"
  git push
  echo "Pushed — Vercel will redeploy in about a minute."
fi
