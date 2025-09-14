FROM python:3.13-slim-bookworm


RUN mkdir /app && \
    useradd --create-home appuser
    
USER root
WORKDIR /app

# Don't be confused here, actual copy filter is done in .dockerignore
COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    chown -R appuser:appuser /app

USER appuser
CMD [ "python", "./app/loki_data_generator/main.py" ]