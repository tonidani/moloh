FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    git \
    clang \
    make \
    cmake \
    sqlite3 \
    ca-certificates \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# build SQLite 3.46 with loadable extensions
RUN wget https://www.sqlite.org/2024/sqlite-autoconf-3460000.tar.gz && \
    tar xvf sqlite-autoconf-3460000.tar.gz && \
    cd sqlite-autoconf-3460000 && \
    ./configure --enable-load-extension --prefix=/usr/local && \
    make -j4 && make install

# build only vss extension
RUN git clone --recursive https://github.com/asg017/sqlite-vss.git && \
    cd sqlite-vss && make loadable-release

RUN mkdir -p /usr/local/lib/sqlite && \
    cp sqlite-vss/dist/release/* /usr/local/lib/sqlite/ 

WORKDIR /workspace/backend

COPY ./backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
COPY ./backend .
RUN chmod +x /workspace/backend/run.sh



