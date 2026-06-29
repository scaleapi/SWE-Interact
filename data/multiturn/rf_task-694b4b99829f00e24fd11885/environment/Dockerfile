FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_trufflesecurity_trufflehog_694b4b99829f00e24fd11885_1.0@sha256:29535eb72b8f6883a83ff50107bf812b5bf1092162ca7a22f7c3d63553f42b5f

COPY repo_exec_server.py /usr/local/bin/repo_exec_server.py

CMD ["sleep", "infinity"]


# Verifier dependency.
RUN set -eux; \
    python3 -m ensurepip --upgrade || true; \
    if command -v apt-get >/dev/null 2>&1; then \
      apt-get update; \
      apt-get install -y --no-install-recommends python3-pip; \
      rm -rf /var/lib/apt/lists/*; \
    fi; \
    python3 -m pip install --no-cache-dir "openai>=1.0,<2.0" "python-dotenv>=1.0" || \
      PIP_BREAK_SYSTEM_PACKAGES=1 python3 -m pip install --no-cache-dir "openai>=1.0,<2.0" "python-dotenv>=1.0"; \
    if [ -x /usr/bin/python3 ] && /usr/bin/python3 -m pip --version >/dev/null 2>&1; then \
      PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0,<2.0" "python-dotenv>=1.0"; \
    fi; \
    python3 -c "import openai, dotenv"; \
    if [ -x /usr/bin/python3 ] && /usr/bin/python3 -m pip --version >/dev/null 2>&1; then /usr/bin/python3 -c "import openai, dotenv"; fi
