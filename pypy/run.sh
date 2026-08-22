#!/bin/bash

# 引数チェック
if [ -z "$1" ]; then
    echo "Usage: ./run.sh FileName.py"
    exit 1
fi

FILENAME=$1

# 1. コンパイルチェック
pypy3 -m py_compile "$FILENAME" || exit 1

# 2. 実行と測定
# 出力を分かりやすく分けるため、区切り線を入れる
echo "------------------------------"


# time の出力をカスタマイズ（フォーマットを指定）
# \n を使って実行結果と時間を物理的に離します
TIMEFORMAT=$'\n------------------------------\nTime:  %R seconds'

time {
    # 2> /dev/null を外すとエラーが見えるようになります
    # 競技中なら 2> /dev/null は消したほうが便利です
    pypy3 -X int_max_str_digits=0 "$FILENAME" <in.txt
}

echo "------------------------------"