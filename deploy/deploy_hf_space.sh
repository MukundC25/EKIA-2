#!/usr/bin/env bash
# Deploy the full EKIA stack (React UI + FastAPI + embedded Neo4j) to a Hugging Face Docker Space.
#
# Usage:   deploy/deploy_hf_space.sh <hf-username>/<space-name>
# Needs:   `hf auth login` done once with a write token (huggingface.co/settings/tokens)
# Then:    in the Space's Settings → "Variables and secrets", add the secrets
#          GROQ_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and the variable LANGFUSE_HOST.
set -euo pipefail

SPACE="${1:?usage: $0 <hf-username>/<space-name>}"
HF="${HF_CLI:-hf}"
ROOT="$(git rev-parse --show-toplevel)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cd "$ROOT"

# Stage tracked + new (non-ignored) files only: .env and local data are gitignored, so they never ship.
git ls-files -co --exclude-standard -z | while IFS= read -r -d '' f; do
  if [ -f "$f" ]; then
    mkdir -p "$STAGE/$(dirname "$f")"
    cp "$f" "$STAGE/$f"
  fi
done

# Belt and braces: never ship secrets or local runtime data.
rm -f "$STAGE/.env"
rm -rf "$STAGE/data/neo4j_data" "$STAGE/data/faiss_index" "$STAGE/data/history.db"

# Spaces build ./Dockerfile and read their settings from the README front matter.
cp Dockerfile.space "$STAGE/Dockerfile"
{ cat deploy/hf-space-header.md; echo; cat README.md; } > "$STAGE/README.md"

"$HF" repo create "$SPACE" --repo-type space --space-sdk docker --public --exist-ok
"$HF" upload "$SPACE" "$STAGE" . --repo-type space \
  --commit-message "Deploy EKIA from $(git rev-parse --short HEAD)"

echo
echo "Deployed: https://huggingface.co/spaces/$SPACE"
