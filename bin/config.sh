#!/usr/bin/env bash

set -eo pipefail

REPO_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd)"

function docker_compose() {
    docker-compose -p pixel-dev -f "$REPO_DIR/docker-compose.yml" "$@"
}
