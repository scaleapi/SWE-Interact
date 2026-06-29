FROM ghcr.io/scaleapi/swe-atlas:swe_atlas_RF_trufflesecurity_trufflehog_696719205599a51110d4b40c_1.0@sha256:c6fcd6e39177b9bd30fe550676e838918544f3ba53b02fb488c3f78f29041e1a

CMD ["sleep", "infinity"]

# Verifier dependency.
RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && rm -rf /var/lib/apt/lists/*
RUN PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --no-cache-dir "openai>=1.0" "python-dotenv>=1.0"
RUN python3 -c "import openai, dotenv" && /usr/bin/python3 -c "import openai, dotenv"
