# syntax=docker/dockerfile:1

# Minimal placeholder image so CI can validate Docker builds
# before the application has anything buildable.
FROM alpine:3.22

# Basic metadata. These can be expanded later with OCI labels,
# build arguments, version information, etc.
LABEL org.opencontainers.image.title="MusicVault"
LABEL org.opencontainers.image.description="MusicVault application container"

WORKDIR /app

# Placeholder file proving the image was built successfully.
RUN printf '%s\n' \
    'MusicVault Docker image built successfully.' \
    'Replace this stub Dockerfile once the application is buildable.' \
    > /app/README.txt

# No application port is exposed yet.
# Add EXPOSE once the backend/frontend service has a defined port.
# Example:
# EXPOSE 5000

# Temporary command so the image can also be run locally.
# Replace this with the real application startup command later.
CMD ["cat", "/app/README.txt"]