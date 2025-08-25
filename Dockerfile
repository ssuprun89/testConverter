FROM python:3.11.0-bullseye
WORKDIR /app
ENV PATH="${PATH}:/root/.local/bin"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      libreoffice \
      libreoffice-java-common \
      default-jre


# Install any needed packages specified in pyproject.toml
RUN pip install poetry

COPY poetry.lock pyproject.toml ./
# disable creating venv
RUN poetry config virtualenvs.create false

# install requirements
RUN poetry install --no-root
# Expose the app port
EXPOSE 8000

# Copy the rest of the app contents and run the app.
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
