FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_grafana_k6_696719205599a51110d4b447_1.0@sha256:d96b70a7d83752867ee2107f03661cdf9756e2064cf13de8da92315aa8b55fab

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
