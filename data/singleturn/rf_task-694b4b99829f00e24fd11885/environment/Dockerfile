FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_trufflesecurity_trufflehog_694b4b99829f00e24fd11885_1.0@sha256:29535eb72b8f6883a83ff50107bf812b5bf1092162ca7a22f7c3d63553f42b5f

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
