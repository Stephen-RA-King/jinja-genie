FROM python:3.11-slim

WORKDIR /app

# Copy the local application and build files to the container
COPY . ./

# Create and activate a virtual environment
RUN ["python", "-m", "venv", "/venv"]
ENV PATH="/venv/bin:$PATH"

# Update the python build tools
RUN ["pip", "install", "--no-cache-dir", "--upgrade", "pip"]

# Install the additional production requirements if any
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

# Now run the entrypoint module
ENTRYPOINT ["/app/entrypoint.py"]
