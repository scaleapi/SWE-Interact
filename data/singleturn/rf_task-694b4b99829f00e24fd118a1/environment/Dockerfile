FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_secdev_scapy_694b4b99829f00e24fd118a1_1.0@sha256:63f1a9702fc2eb7ea14c3396b9ee8b51c3b039cb2fe31f6c806c76b7ed15a91f

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
