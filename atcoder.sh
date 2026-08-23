#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  ./atcoder.sh login
  ./atcoder.sh download FILE.py
  ./atcoder.sh test --lang {codon|pypy} FILE.py
  ./atcoder.sh submit --lang {codon|pypy} [--yes] FILE.py
  ./atcoder.sh languages FILE.py

FILE.py must be placed at contests/CONTEST/TASK.py (or .contests/...).
For example, contests/abc472/a.py maps to:
https://atcoder.jp/contests/abc472/tasks/abc472_a
EOF
}

die() {
    echo "error: $*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "'$1' is not installed; rebuild the dev container"
}

command_name=${1:-}
[[ -n "$command_name" ]] || { usage; exit 2; }
shift

if [[ "$command_name" == "login" ]]; then
    [[ $# -eq 0 ]] || die "login takes no arguments"
    require_command oj
    exec oj login https://atcoder.jp/
fi

lang=""
assume_yes=false
source_file=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --lang)
            [[ $# -ge 2 ]] || die "--lang requires codon or pypy"
            lang=$2
            shift 2
            ;;
        --yes|-y)
            assume_yes=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            die "unknown option: $1"
            ;;
        *)
            [[ -z "$source_file" ]] || die "only one source file can be specified"
            source_file=$1
            shift
            ;;
    esac
done

[[ -n "$source_file" ]] || die "a source file is required"
[[ -f "$source_file" ]] || die "source file not found: $source_file"
[[ "$source_file" == *.py ]] || die "source file must have a .py extension"

source_dir=$(cd "$(dirname "$source_file")" && pwd)
source_file="$source_dir/$(basename "$source_file")"
contest=$(basename "$source_dir")
task=$(basename "$source_file" .py)

contest=${contest,,}
task=${task,,}
[[ "$contest" =~ ^[a-z0-9_-]+$ ]] || die "invalid contest name: $contest"
[[ "$task" =~ ^[a-z0-9_-]+$ ]] || die "invalid task name: $task"

if [[ "$task" == "${contest}_"* ]]; then
    task_id=$task
else
    task_id="${contest}_${task}"
fi

problem_url="https://atcoder.jp/contests/${contest}/tasks/${task_id}"
test_dir="$source_dir/test/$task"

download_samples() {
    require_command oj
    mkdir -p "$test_dir"
    oj download "$problem_url" --directory "$test_dir"
}

case "$command_name" in
    download)
        download_samples
        ;;
    test)
        [[ "$lang" == "codon" || "$lang" == "pypy" ]] || die "test requires --lang codon or --lang pypy"
        require_command oj

        if ! compgen -G "$test_dir/*.in" >/dev/null; then
            echo "No samples found; downloading from $problem_url"
            download_samples
        fi

        if [[ "$lang" == "pypy" ]]; then
            require_command pypy3
            printf -v quoted_source '%q' "$source_file"
            oj test --directory "$test_dir" --command "pypy3 -X int_max_str_digits=0 $quoted_source"
        else
            require_command codon
            executable=$(mktemp "${TMPDIR:-/tmp}/atcoder-codon.XXXXXX")
            trap 'rm -f "$executable"' EXIT
            codon build --release -o "$executable" "$source_file"
            printf -v quoted_executable '%q' "$executable"
            oj test --directory "$test_dir" --command "$quoted_executable"
        fi
        ;;
    languages)
        require_command oj-api
        require_command jq
        oj-api get-problem --full "$problem_url" |
            jq -r '.result.availableLanguages[] | [.id, .description] | @tsv'
        ;;
    submit)
        [[ "$lang" == "codon" || "$lang" == "pypy" ]] || die "submit requires --lang codon or --lang pypy"
        require_command oj-api
        require_command jq

        case "$lang" in
            codon) language_prefix='Python (Codon ' ;;
            pypy)  language_prefix='Python (PyPy ' ;;
        esac

        problem_json=$(oj-api get-problem --full "$problem_url")
        language_id=$(
            jq -r --arg prefix "$language_prefix" '
                [.result.availableLanguages[]
                 | select(.description | startswith($prefix))]
                | if length == 1 then .[0].id else empty end
            ' <<<"$problem_json"
        )
        [[ -n "$language_id" ]] || die "could not uniquely resolve a language starting with '$language_prefix'; run the languages command"

        language_description=$(
            jq -r --arg id "$language_id" '
                .result.availableLanguages[]
                | select((.id | tostring) == $id)
                | .description
            ' <<<"$problem_json"
        )

        echo "Problem:  $problem_url"
        echo "Source:   $source_file"
        echo "Language: $language_description (ID: $language_id)"

        if [[ "$assume_yes" != true ]]; then
            read -r -p "Submit? [y/N] " answer
            [[ "$answer" == "y" || "$answer" == "Y" ]] || { echo "Canceled."; exit 0; }
        fi

        oj-api submit-code "$problem_url" --file "$source_file" --language "$language_id"
        ;;
    *)
        usage
        die "unknown command: $command_name"
        ;;
esac
