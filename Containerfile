FROM registry.access.redhat.com/ubi9/python-312-minimal:9.8

ARG VCS_REF=uncommitted
ARG APP_VERSION="0.3.0"
ARG SOURCE_URL=""
LABEL org.opencontainers.image.title="OpenShift Health API" \
      org.opencontainers.image.description="Health and diagnostics API for OpenShift" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="${SOURCE_URL}"

WORKDIR /opt/app-root/src
COPY requirements.txt ./
USER 0
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && rpm --erase --nodeps curl-minimal libcurl-minimal \
    && rm -rf /var/cache/yum
COPY --chown=1001:0 app ./app

ENV SERVICE_NAME=openshift-health-api \
    SERVICE_VERSION=${APP_VERSION} \
    MIN_FREE_DISK_MB=64 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER 1001
EXPOSE 8080
STOPSIGNAL SIGTERM
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log", "--log-config", "app/uvicorn-logging.json"]
