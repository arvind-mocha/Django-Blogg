FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir -p /app/data/media /app/staticfiles \
    && chown -R app:app /app/data /app/staticfiles

COPY --chown=app:app manage.py ./
COPY --chown=app:app Mysite ./Mysite
COPY --chown=app:app blog ./blog
COPY --chown=app:app usersapp ./usersapp
COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/blog-entrypoint

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 8000), timeout=3).close()"
ENTRYPOINT ["blog-entrypoint"]
CMD ["gunicorn", "Mysite.wsgi:application", "--bind=0.0.0.0:8000", "--workers=1", "--threads=4", "--timeout=30", "--access-logfile=-", "--access-logformat=%(m)s %(s)s %(L)s", "--error-logfile=-", "--forwarded-allow-ips="]
