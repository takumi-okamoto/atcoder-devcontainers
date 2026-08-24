# AtCoder development container

リポジトリのルートを VS Code で開き、コマンドパレットから
`Dev Containers: Reopen in Container` を実行すると、PyPy 3.11とCodon 0.19.3の
両方を利用できる共通環境が起動します。

処理系ごとにコンテナを切り替える必要はありません。コンテナ内ではリポジトリ全体が
`/workspace` にマウントされます。
たとえば、各環境の実行スクリプトは次のように利用できます。

```bash
cd /workspace/codon
./run.sh main.py
```

```bash
cd /workspace/pypy
./run.sh main.py
```

イメージ設定を変更した場合は、コマンドパレットから
`Dev Containers: Rebuild and Reopen in Container` を実行してください。

## AtCoderのサンプルテストと提出

`online-judge-tools` は共通のDev Containerに導入されています。初回のみAtCoderへログインします。

```bash
./atcoder.sh login
```

解答は `contests/<contest>/<task>.py` に置きます（`.contests/...` でも利用できます）。たとえば
`contests/abc472/a.py` は `https://atcoder.jp/contests/abc472/tasks/abc472_a` に対応します。

```bash
# サンプルを取得（test/a/ 以下に保存）
./atcoder.sh download contests/abc472/a.py

# 選択した処理系でサンプルを実行
./atcoder.sh test --lang codon contests/abc472/a.py
./atcoder.sh test --lang pypy contests/abc472/a.py

# 選択したAtCoder言語で提出（提出前に確認あり）
./atcoder.sh submit --lang codon contests/abc472/a.py
./atcoder.sh submit --lang pypy contests/abc472/a.py
```

`--yes`（または `-y`）を付けると提出前の確認を省略できます。

```bash
./atcoder.sh submit --lang codon --yes contests/abc472/a.py
```

CodonとPyPyはどちらも拡張子が `.py` のため、提出言語を拡張子から判定しません。問題ページの
利用可能言語から `Python (Codon ...)` または `Python (PyPy ...)` の言語IDを動的に取得します。
確認したい場合は次を実行します。

```bash
./atcoder.sh languages contests/abc472/a.py
```

Dockerfileを変更した後は `Dev Containers: Rebuild and Reopen in Container` を実行してください。
