FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PINTARAI_DB=/app/runtime/pintarai.sqlite3
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt && \
    useradd --create-home --uid 10001 pintarai && mkdir -p /app/runtime && chown -R pintarai:pintarai /app/runtime
COPY --chown=pintarai:pintarai backend /app/backend
COPY --chown=pintarai:pintarai web /app/web
COPY --chown=pintarai:pintarai data/lessons_draft.json data/audit_evidence_v1.8.json /app/data/
USER pintarai
EXPOSE 8000
# Render sets PORT, while running locally defaults to 8000.
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
