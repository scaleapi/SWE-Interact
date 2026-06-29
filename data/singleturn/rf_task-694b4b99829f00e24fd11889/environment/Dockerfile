FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_trufflesecurity_trufflehog_694b4b99829f00e24fd11889_1.0@sha256:68f800df9360a8b9aac766a3f2345a70899f127fa4d7c0b78961c7ca72ea48f4

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
