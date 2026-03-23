#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${ROOT_DIR}/skills"
COMMUNITY_DIR="${SKILLS_DIR}/community"

mkdir -p "${COMMUNITY_DIR}"

echo "Installing local Python dependencies for skills..."
python3 -m pip install --upgrade pip
python3 -m pip install requests beautifulsoup4 firecrawl-py

echo "Registering community skill repositories..."
if [[ ! -d "${COMMUNITY_DIR}/openclaw-agent-router" ]]; then
  git clone https://github.com/openclaw-ai/agent-router.git "${COMMUNITY_DIR}/openclaw-agent-router"
else
  git -C "${COMMUNITY_DIR}/openclaw-agent-router" pull --ff-only
fi

if [[ ! -d "${COMMUNITY_DIR}/openclaw-self-improve" ]]; then
  git clone https://github.com/openclaw-ai/self-improve.git "${COMMUNITY_DIR}/openclaw-self-improve"
else
  git -C "${COMMUNITY_DIR}/openclaw-self-improve" pull --ff-only
fi

echo "Skills installation complete."
