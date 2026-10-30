FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd \
    --gid 10001 \
    appgroup \
    && useradd \
    --uid 10001 \
    --gid appgroup \
    --create-home \
    appuser

COPY requirements.txt ./requirements.txt

RUN python -m pip install \
    --no-cache-dir \
    --upgrade pip \
    && python -m pip install \
    --no-cache-dir \
    -r requirements.txt

COPY --chown=appuser:appgroup app ./app

RUN mkdir -p /app/app/static/uploads \
    && chown -R appuser:appgroup \
    /app/app/static/uploads

USER appuser

EXPOSE 5055

CMD ["gunicorn", "--bind=0.0.0.0:5055", "--workers=2", "--threads=4", "--timeout=120", "--access-logfile=-", "--error-logfile=-", "--worker-tmp-dir=/dev/shm", "app:create_app()"]