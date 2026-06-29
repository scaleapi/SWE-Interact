FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_grafana_k6_696719205599a51110d4b436_1.0@sha256:8a8ff0dfe3c9c5430f3b876fd167a4239e0760e8ceabb3c2525af50d4df0a442

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
