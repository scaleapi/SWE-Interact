FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_Automattic_wp-calypso_696719205599a51110d4b434_1.0@sha256:6b1f28b1fae730c0d00b2acdb6f68a32b270468fbbb4ec4581db62e0d3b0c887

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
