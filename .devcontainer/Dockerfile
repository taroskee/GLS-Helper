# .devcontainer/Dockerfile

# --- Node.js Stage ---
FROM node:22-bookworm-slim AS node-source

# --- Python Stage ---
FROM python:3.13-slim-bookworm

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# 1. OSパッケージ (Zsh, fonts-powerline を追加)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    sqlite3 \
    less \
    zsh \
    fonts-powerline \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Node.js の導入
COPY --from=node-source /usr/local/bin/node /usr/local/bin/
COPY --from=node-source /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && ln -s /usr/local/lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack

# 3. ユーザー作成 (デフォルトシェルを /bin/zsh に変更)
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -s /bin/zsh -m $USERNAME

# 4. ワークスペース設定
WORKDIR /workspace

# --- ここから Zsh & Oh My Zsh 設定 ---
USER $USERNAME

# Oh My Zsh のインストール (Unattended)
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# プラグインのインストール (自動補完 & ハイライト)
RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions \
    && git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# .zshrc の設定変更 (プラグイン有効化)
RUN sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc