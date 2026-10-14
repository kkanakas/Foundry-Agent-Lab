#!/usr/bin/env zsh
set -euo pipefail

REPO_DIR="${0:A:h:h}"
FIXTURE="$(mktemp -d "${TMPDIR:-/tmp}/foundry-shell.XXXXXXXX")"
FIXTURE="${FIXTURE:A}"
export MOCK_CALLS="$FIXTURE/calls"
export MOCK_SERVER_PID="$FIXTURE/server-pid"

cleanup() {
    if [[ -f "$MOCK_SERVER_PID" ]]; then
        kill "$(<"$MOCK_SERVER_PID")" 2>/dev/null || true
    fi
    find "$FIXTURE" -depth -delete
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

expect_exit() {
    local expected="$1" actual=0
    shift
    "$@" >"$FIXTURE/output" 2>&1 || actual=$?
    [[ "$actual" == "$expected" ]] || fail "$*: expected exit $expected, got $actual"
}

ROOT="$FIXTURE/repo with spaces"
mkdir -p "$ROOT"
scripts=("$REPO_DIR"/*.sh "$REPO_DIR"/*-demo/*.sh)
for script in "${scripts[@]}"; do
    zsh -n "$script"
    relative="${script#"$REPO_DIR"/}"
    mkdir -p "$ROOT/${relative:h}"
    cp "$script" "$ROOT/$relative"
    [[ -x "$script" ]] || fail "$relative is not executable"
done

cd "$FIXTURE"
for script in "$ROOT"/*.sh "$ROOT"/*-demo/*.sh; do
    expect_exit 1 "$script"
    grep -q 'Missing virtual environment' "$FIXTURE/output" ||
        fail "$script did not report the missing virtual environment"
done

mkdir -p "$ROOT/.venv/bin"
cat >"$ROOT/.venv/bin/python" <<'MOCK'
#!/usr/bin/env zsh
set -euo pipefail
printf '%s|%s\n' "$*" "${LOG_FILE:-}" >>"$MOCK_CALLS"
case "$1" in
    */create_agent.py) exit "${MOCK_CREATE_EXIT:-0}" ;;
    */chat.py) exit "${MOCK_CHAT_EXIT:-0}" ;;
    */main.py)
        printf '%s\n' "$$" >"$MOCK_SERVER_PID"
        exec sleep 60
        ;;
    -)
        cat >/dev/null
        exit "${MOCK_INLINE_EXIT:-0}"
        ;;
    *) printf 'Unexpected mock invocation: %s\n' "$*" >&2; exit 99 ;;
esac
MOCK
chmod +x "$ROOT/.venv/bin/python"

assert_server_stopped() {
    [[ -f "$MOCK_SERVER_PID" ]] || fail 'Hosted server was not started'
    local pid="$(<"$MOCK_SERVER_PID")"
    if kill -0 "$pid" 2>/dev/null; then
        fail "Hosted server $pid was not stopped"
    fi
    rm "$MOCK_SERVER_PID"
}

for script in "$ROOT"/*.sh "$ROOT"/*-demo/demo.sh; do
    : >"$MOCK_CALLS"
    expect_exit 0 "$script" log
    grep -q '/chat.py|' "$MOCK_CALLS" || fail "$script did not launch chat"
    grep -q '/chat-log.txt$' "$MOCK_CALLS" || fail "$script did not enable logging"
    if [[ -f "$MOCK_SERVER_PID" ]]; then
        assert_server_stopped
    fi
    : >"$MOCK_CALLS"
    expect_exit 0 env LOG_FILE=stale "$script"
    grep -q '/chat.py|$' "$MOCK_CALLS" || fail "$script did not clear logging"
    if [[ -f "$MOCK_SERVER_PID" ]]; then
        assert_server_stopped
    fi
    expect_exit 7 env MOCK_CHAT_EXIT=7 "$script"
    if [[ -f "$MOCK_SERVER_PID" ]]; then
        assert_server_stopped
    fi
    if [[ "$script" != *hosted* ]]; then
        : >"$MOCK_CALLS"
        expect_exit 9 env MOCK_CREATE_EXIT=9 "$script"
        if grep -q '/chat.py|' "$MOCK_CALLS"; then
            fail "$script ran chat after agent creation failed"
        fi
    fi
done

for script in "$ROOT"/*-demo/reset.sh; do
    : >"$MOCK_CALLS"
    expect_exit 0 "$script"
    grep -q "^- ${script:h}|" "$MOCK_CALLS" ||
        fail "$script did not pass its directory to the reset code"
done

expect_exit 8 env MOCK_INLINE_EXIT=8 "$ROOT/8-hosted-demo.sh"
[[ ! -f "$MOCK_SERVER_PID" ]] || fail 'Hosted server started after preflight failed'
printf 'PASS: %d shell scripts; launch, logging, reset, and failure checks.\n' "${#scripts[@]}"
