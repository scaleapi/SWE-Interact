FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_grafana_grafana_696719205599a51110d4b455_1.0@sha256:3fe50147daa3cbe3e56dd7879fa1b7625c129d6f89bca4ab9d07c5040d6ef9c4

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
