FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_MariaDB_server_69d196f015a150488265afc1_1.0@sha256:2d91b0ab5cefe39ef357005ee8d7cf526d2d4440dd7c658816ce7f6c3745e3c6

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
