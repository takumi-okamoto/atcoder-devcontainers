#!/bin/bash

# 引数（ファイル名）がない場合はエラーを出して終了
if [ -z "$1" ]; then
    echo "Usage: ./run.sh FileName.py"
    exit 1
fi

# $1 は 1番目の引数（ファイル名）に置き換わります
FILENAME=$1

# コンパイルチェック
export CODON_PYTHON=/usr/local/lib/libpython3.13.so
codon build --release -o a.out "$FILENAME"

# 2. 実行と測定
# 出力を分かりやすく分けるため、区切り線を入れる
echo "------------------------------"

# time の出力をカスタマイズ（フォーマットを指定）
# \n を使って実行結果と時間を物理的に離します
TIMEFORMAT=$'\n------------------------------\nTime:  %R seconds'

time {
    # 実行して結果を表示
    ./a.out <in.txt
}

echo "------------------------------"

rm a.out