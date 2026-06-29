FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_netdata_netdata_69b7c2a04b6f8ff9ed98813d_1.0@sha256:6193ba7e853950a21a0f1335e189973972cad879656d2f42f41192939583b8a9

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
