FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_OISF_suricata_69b7c2a04b6f8ff9ed98812f_1.0@sha256:c546c5879339a820bf6ddf165e22fcfa1d146e0115a7b96487961b9c8e0161a3

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
