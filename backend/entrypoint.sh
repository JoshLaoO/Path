#!/bin/sh
set -e
# Ensure appuser can write to the mounted volume
chown -R appuser:appuser /data 2>/dev/null || true
exec gosu appuser "$@"
