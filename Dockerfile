FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Install dependencies
RUN uv sync --no-dev

# Expose port
EXPOSE 8183

# Run server
CMD ["uv", "run", "uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8183"]
