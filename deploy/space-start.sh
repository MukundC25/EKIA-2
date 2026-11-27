#!/bin/sh
# Hugging Face Space entrypoint: start the embedded Neo4j, wait until it is ready, then start EKIA.
set -e

if [ "${NEO4J_EMBEDDED:-true}" = "true" ]; then
  # Fresh random password on every start; it never leaves the container.
  NEO4J_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(24))')"
  export NEO4J_PASSWORD
  export NEO4J_URI="bolt://127.0.0.1:7687"
  export NEO4J_USERNAME="neo4j"

  rm -rf "$NEO4J_HOME/data/dbms/auth.ini" 2>/dev/null || true
  "$NEO4J_HOME/bin/neo4j-admin" dbms set-initial-password "$NEO4J_PASSWORD" >/dev/null
  "$NEO4J_HOME/bin/neo4j" start

  echo "[start] Waiting for Neo4j..."
  i=0
  until curl -s -o /dev/null http://127.0.0.1:7474; do
    i=$((i + 1))
    if [ "$i" -ge 90 ]; then
      echo "[start] Neo4j did not start in time; continuing (the app retries automatically)."
      tail -n 40 "$NEO4J_HOME/logs/neo4j.log" 2>/dev/null || true
      break
    fi
    sleep 1
  done
  echo "[start] Neo4j is up."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-7860}"
