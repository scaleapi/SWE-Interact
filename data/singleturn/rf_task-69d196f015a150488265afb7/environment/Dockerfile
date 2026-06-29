FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_secdev_scapy_69d196f015a150488265afb7_1.0@sha256:fbe2d0aef1129b37a45dc6e8ce85e715f150c1c45a0575d30d0364499d5ea6f9

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
