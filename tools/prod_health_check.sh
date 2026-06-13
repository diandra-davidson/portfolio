#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://portfolio.diandrad.dev}"
CALLBACK_URL="${2:-${BASE_URL%/}/oauth/callback}"

failures=0

print_ok() {
  printf 'OK   %s\n' "$1"
}

print_fail() {
  printf 'FAIL %s\n' "$1"
  failures=$((failures + 1))
}

check_health() {
  local url="${BASE_URL%/}/nginx-health"
  local body
  if ! body="$(curl -fsS "$url")"; then
    print_fail "NGINX health endpoint unreachable: $url"
    return
  fi

  if [[ "$body" == "ok" || "$body" == $'ok\n' ]]; then
    print_ok "NGINX health endpoint returned ok"
  else
    print_fail "NGINX health endpoint returned unexpected body: $body"
  fi
}

check_home() {
  local url="${BASE_URL%/}/"
  local code
  if ! code="$(curl -sS -o /dev/null -w "%{http_code}" "$url")"; then
    print_fail "Home page unreachable: $url"
    return
  fi

  if [[ "$code" == "200" ]]; then
    print_ok "Home page returned HTTP 200"
  else
    print_fail "Home page returned HTTP $code"
  fi
}

check_oauth_redirect() {
  local url="${BASE_URL%/}/fetch/github_metadata"
  local headers
  local status_line
  local location

  if ! headers="$(curl -sSI "$url")"; then
    print_fail "OAuth start endpoint unreachable: $url"
    return
  fi

  status_line="$(printf '%s\n' "$headers" | head -n 1 | tr -d '\r')"
  location="$(printf '%s\n' "$headers" | awk 'BEGIN{IGNORECASE=1} /^location:/{print $2}' | tr -d '\r')"

  if [[ "$status_line" != *" 302 "* && "$status_line" != *" 301 "* ]]; then
    print_fail "OAuth start did not redirect (status: $status_line)"
    return
  fi

  if [[ "$location" != https://github.com/login/oauth/authorize* ]]; then
    print_fail "OAuth redirect target is not GitHub authorize endpoint: $location"
    return
  fi

  if [[ "$location" == *"redirect_uri="* ]]; then
    print_ok "OAuth start redirects to GitHub authorize endpoint"
  else
    print_fail "OAuth redirect missing redirect_uri query parameter"
  fi

  local encoded_callback
  encoded_callback="$(python3 - <<'PY'
import urllib.parse
import os
print(urllib.parse.quote(os.environ['CALLBACK_URL'], safe=''))
PY
)"

  if [[ "$location" == *"redirect_uri=${encoded_callback}"* ]]; then
    print_ok "OAuth redirect_uri matches expected callback URL"
  else
    print_fail "OAuth redirect_uri does not match expected callback URL"
    printf '     expected: %s\n' "$CALLBACK_URL"
  fi
}

printf 'Running production checks for %s\n' "$BASE_URL"
printf 'Expected OAuth callback: %s\n' "$CALLBACK_URL"

export CALLBACK_URL

check_health
check_home
check_oauth_redirect

if (( failures > 0 )); then
  printf '\nResult: %d check(s) failed\n' "$failures"
  exit 1
fi

printf '\nResult: all checks passed\n'
