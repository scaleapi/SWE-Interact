FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_netdata_netdata_69b7c2a04b6f8ff9ed98813b_1.0@sha256:f0f262c96c031204c1a0f2b313ec74629dce84aa32aa2e1e4fdf068fccf2a0b4

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
