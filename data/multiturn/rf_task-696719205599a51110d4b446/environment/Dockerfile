FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_grafana_k6_696719205599a51110d4b446_1.0@sha256:de3821109167af1d24a8ce3207b14a6840ee11aea0909c838c471fd9b2c372b5

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
