FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_Automattic_wp-calypso_694b4b99829f00e24fd11891_1.0@sha256:0dd613c90d6bcfc266fb8f266d350d5e6236872425bf86d022c1847b28a5d6d3

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
