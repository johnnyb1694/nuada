# Create image in accordance with the current Python version
ARG PYTHON_VERSION=3.10.12
FROM python:${PYTHON_VERSION}-slim

# Stop Python from writing extraneous data to disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory for pipeline application
WORKDIR /pipeline

# Initialise a specific runtime service account which has no ability to login or amend permissions within a container context
ARG UID=10001
RUN adduser \
    --gecos '' \
    --disabled-password \
    --home "/nonexistent" \
    --shell '/sbin/nologin' \
    --no-create-home \
    --uid "${UID}" \
    nuada_pipeline 

# (i) Bind-mount the requirements file from path `source` into the container at path `target` (avoids having to copy `requirements.txt` into the container)
# (ii) Create package cache for Python dependencies in container at path `target`
# NB: if this layer needs to be rebuilt, it will use the `pip` cache inside `/root/.cache/pip`
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Set the user profile for any commands which follow
USER nuada_pipeline

# Copy the remainder of all required source code for the data pipeline
COPY . .

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["/bin/bash"]