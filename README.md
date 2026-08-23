# AtCoder development containers

リポジトリのルートを VS Code で開き、コマンドパレットから
`Dev Containers: Reopen in Container` を実行すると、次の環境を選択できます。

- `AtCoder (Codon 0.19.3)`
- `AtCoder (PyPy 3.11)`

環境を切り替えるときは、コマンドパレットから
`Dev Containers: Switch Container` を実行し、もう一方の環境を選択します。
VS Code は同じウィンドウを選択した Compose サービスへ再接続します。

コンテナ内ではリポジトリ全体が `/workspace` にマウントされます。
たとえば、各環境の実行スクリプトは次のように利用できます。

```bash
cd /workspace/codon
./run.sh main.py
```

```bash
cd /workspace/pypy
./run.sh main.py
```

イメージや Compose 設定を変更した場合は、コマンドパレットから
`Dev Containers: Rebuild and Reopen in Container` を実行してください。

両方のサービスは、すばやく切り替えられるよう VS Code を閉じた後も起動したままです。
停止するときは、ホスト側で次を実行します。

```bash
docker compose -f .devcontainer/compose.yaml down
```
