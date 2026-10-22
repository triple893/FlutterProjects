#!/usr/bin/env bash
# Switch every searchable collection to the trigram tokenizer so Japanese text
# matches mid-word (default "porter unicode61" only matches from the start of a run).
# Queries shorter than 3 characters still return nothing.
#
# Usage: EMDASH_COOKIE_JAR=cookies.txt scripts/enable-ja-search.sh [base-url]
#   The cookie jar must hold an admin session (locally: /_emdash/api/setup/dev-bypass).
set -euo pipefail

BASE="${1:-http://127.0.0.1:4321}"
JAR="${EMDASH_COOKIE_JAR:?set EMDASH_COOKIE_JAR to a cookie jar with an admin session}"

for collection in labs agents posts pages; do
	curl -sS -b "$JAR" -X POST "$BASE/_emdash/api/search/enable" \
		-H "Content-Type: application/json" \
		-H "Origin: $BASE" \
		-H "X-EmDash-Request: 1" \
		-d "{\"collection\":\"$collection\",\"enabled\":true,\"tokenize\":\"trigram\"}"
	echo
done
