# AtCoderのジャッジ環境に近いと思われる Ubuntu を使用
FROM ubuntu:24.04

# 環境変数（インタラクティブな入力を無効化）
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# 1. 依存ライブラリのインストール
RUN apt-get update && apt-get install -y \
    git wget bzip2 build-essential gfortran \
    libopenblas-dev liblapack-dev pkg-config libgeos-dev meson \
    curl jq python3-venv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# AtCoder のサンプル取得・テスト・提出用 CLI。
# PyPy のパッケージ群とは分離し、ツール自体は CPython で動かします。
RUN python3 -m venv /opt/online-judge-tools \
    && /opt/online-judge-tools/bin/pip install --no-cache-dir online-judge-tools \
    && ln -s /opt/online-judge-tools/bin/oj /usr/local/bin/oj \
    && ln -s /opt/online-judge-tools/bin/oj-api /usr/local/bin/oj-api

# 2. PyPy3.11 バイナリのインストール
WORKDIR /tmp
RUN wget https://downloads.python.org/pypy/pypy3.11-v7.3.20-linux64.tar.bz2 \
    && tar jxvf pypy3.11-v7.3.20-linux64.tar.bz2 \
    && cd pypy3.11-v7.3.20-linux64 \
    && ./bin/pypy3 -m ensurepip \
    && ./bin/pip3 install --upgrade pip \
    # パスが通る場所へコピー
    && cp -r ./bin/* /usr/local/bin/ \
    && cp -r ./include/* /usr/local/include/ \
    && cp -r ./lib/* /usr/local/lib/ \
    # 元データを削除して軽量化
    && cd /tmp && rm -rf pypy3.11-v7.3.20-linux64*

# 3. 各種ライブラリのインストール
# ※ AtCoder環境を再現するため一括インストール
RUN pypy3 -m pip install --break-system-packages \
    numpy==2.3.2 \
    # scipy==1.15.3 \
    # networkx==3.5 \
    # sympy==1.14.0 \
    sortedcontainers==2.4.0 \
    more-itertools==10.7.0 \
    # shapely==2.1.1 \
    # bitarray==3.6.0 \
    # PuLP==3.2.2 \
    # mpmath==1.3.0 \
    # pandas==2.3.1 \
    # z3-solver==4.15.1.0 \
    # scikit-learn==1.7.1 \
    # cppyy==3.5.0 \
    acl-cpp-python==0.6.2 \
    git+https://github.com/not522/ac-library-python@27fdbb71cd0d566bdeb12746db59c9d908c6b5d5

# 作業ディレクトリの設定
WORKDIR /workspace
