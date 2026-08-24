FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV CODON_PYTHON=/usr/local/lib/libpython3.13.so

# PyPy、Codon、CPythonのビルドと実行に必要なOSパッケージを共通化します。
RUN apt-get update && apt-get install -y \
    ansifilter build-essential bzip2 curl git gfortran jq lcov locales \
    libbz2-dev libffi-dev libgdbm-compat-dev libgdbm-dev libgeos-dev \
    liblapack-dev liblzma-dev libncurses5-dev libopenblas-dev \
    libreadline6-dev libsqlite3-dev libssl-dev llvm-18-dev llvm-bolt \
    lzma lzma-dev meson pkg-config python3-venv tk-dev uuid-dev wget \
    zlib1g-dev \
    && locale-gen en_US.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ここからは、変更頻度が低くビルドコストが高い処理を先に置きます。
# 後段のツールやライブラリを変更しても、処理系の構築キャッシュを再利用できます。
WORKDIR /tmp

# Codonから利用するCPython 3.13.7
RUN wget -q https://www.python.org/ftp/python/3.13.7/Python-3.13.7.tar.xz \
    && tar xf Python-3.13.7.tar.xz \
    && cd Python-3.13.7 \
    && ln -s /usr/lib/llvm-18/lib/libbolt_rt_instr.a /usr/lib/libbolt_rt_instr.a \
    && ./configure --enable-optimizations --with-lto=full --with-strict-overflow --enable-bolt --enable-shared \
    && make -j"$(nproc)" \
    && make altinstall \
    && ldconfig \
    && cd /tmp \
    && rm -rf Python-3.13.7*

# Numbaなどのビルドに使うCPython側のパッケージ管理ツールを先に準備します。
RUN python3.13 -m pip install --upgrade setuptools pip

# PyPy 3.11
RUN wget -q https://downloads.python.org/pypy/pypy3.11-v7.3.20-linux64.tar.bz2 \
    && tar jxf pypy3.11-v7.3.20-linux64.tar.bz2 \
    && cd pypy3.11-v7.3.20-linux64 \
    && ./bin/pypy3 -m ensurepip \
    && ./bin/pip3 install --upgrade pip \
    && cp -r ./bin/* /usr/local/bin/ \
    && cp -r ./include/* /usr/local/include/ \
    && cp -r ./lib/* /usr/local/lib/ \
    && cd /tmp \
    && rm -rf pypy3.11-v7.3.20-linux64*

# Codon 0.19.3
RUN wget -q https://github.com/exaloop/codon/releases/download/v0.19.3/codon-linux-x86_64.tar.gz \
    && tar -C /usr/local --strip-components=1 -xf codon-linux-x86_64.tar.gz \
    && rm codon-linux-x86_64.tar.gz

# Numbaもビルドコストが高く変更頻度が低いため、通常のライブラリより先に置きます。
RUN wget -q -O numba.tar.gz https://files.pythonhosted.org/packages/1c/a0/e21f57604304aa03ebb8e098429222722ad99176a4f979d34af1d1ee80da/numba-0.61.2.tar.gz \
    && mkdir numba \
    && tar -C numba --strip-components=1 -xf numba.tar.gz \
    && cd numba \
    && sed -i 's/ext_cuda_extras, //' setup.py \
    && rm -rf numba/cuda \
    && python3.13 -m pip install . \
    && cd /tmp \
    && rm -rf numba*

# ここからは、比較的変更しやすく再構築コストが低いツールとライブラリです。

# AtCoderのサンプル取得・テスト・提出用CLIは専用のCPython環境で動かします。
RUN /usr/bin/python3 -m venv /opt/online-judge-tools \
    && /opt/online-judge-tools/bin/pip install --no-cache-dir \
        online-judge-tools setuptools==75.8.2 \
    && ln -s /opt/online-judge-tools/bin/oj /usr/local/bin/oj \
    && ln -s /opt/online-judge-tools/bin/oj-api /usr/local/bin/oj-api

# PyPy向けライブラリ
# AtCoder環境に含まれるパッケージ一覧をコメントとして残しています。
# ビルド時間を抑えるため、実際に使うものだけをコメント解除してインストールします。
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

# Codon/CPython向けライブラリ
# AtCoder環境に含まれるパッケージ一覧をコメントとして残しています。
# ビルド時間を抑えるため、実際に使うものだけをコメント解除してインストールします。
RUN python3.13 -m pip install --no-warn-script-location \
        absl-py==2.3.1 \
        bitarray==3.6.1 \
        # cppyy==3.5.0 \
        # cppyy-backend==1.15.3 \
        # cppyy-cling==6.32.8 \
        # CPyCppyy==1.13.0 \
        # Cython==3.1.3 \
        # filelock==3.19.1 \
        # fsspec==2025.7.0 \
        # gmpy2==2.2.1 \
        immutabledict==4.2.1 \
        # Jinja2==3.1.6 \
        # joblib==1.5.1 \
        # lightgbm==4.6.0 \
        # llvmlite==0.44.0 \
        # MarkupSafe==3.0.2 \
        more-itertools==10.7.0 \
        # mpmath==1.3.0 \
        # networkx==3.5 \
        # numpy==2.2.6 \
        # ortools==9.14.6206 \
        # pandas==2.3.2 \
        # polars==1.31.0 \
        # protobuf==6.31.1 \
        # PuLP==3.2.2 \
        # pyrsistent==0.20.0 \
        # python-dateutil==2.9.0.post0 \
        # pytz==2025.2 \
        # rustworkx==0.16.0 \
        # scikit-learn==1.7.1 \
        # scipy==1.16.1 \
        # shapely==2.1.1 \
        # six==1.17.0 \
        sortedcontainers==2.4.0 \
        # sympy==1.14.0 \
        # threadpoolctl==3.6.0 \
        typing_extensions==4.14.1 \
        # tzdata==2025.2 \
        # z3-solver==4.15.3.0 \
        git+https://github.com/not522/ac-library-python@27fdbb71cd0d566bdeb12746db59c9d908c6b5d5 \
        acl-cpp-python==0.6.2

# AtCoder環境には次のパッケージも含まれますが、サイズとビルド時間を考慮して導入しません。
# torch==2.8.0+cpu --index-url https://download.pytorch.org/whl/cpu

WORKDIR /workspace
