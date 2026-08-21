# Image cho pipeline huan luyen / cham diem SUBSCRIPTION.
# Build tu THU MUC GOC repo:  docker build -f ml/Dockerfile -t wealify-ml .
FROM python:3.11-slim

WORKDIR /app

COPY ml/requirements.txt /app/ml/requirements.txt
RUN pip install --no-cache-dir -r /app/ml/requirements.txt

COPY ml/ /app/ml/

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "ml.cli"]
CMD ["versions"]
