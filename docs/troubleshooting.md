# Troubleshooting

- Startup configuration error: verify booleans, URL schemes, numeric ranges, and log level.
- `/readyz` is 503: inspect safe check names and internal application logs; dependency addresses are intentionally absent.
- Disk/temp failure in OpenShift: verify the `/tmp` `emptyDir` mount and quota.
- Container exits under a random UID: confirm the image was built from `Containerfile` and `/tmp` is writable.
- Route unavailable: check namespace, Service endpoints, pod readiness, and Route admission.
- No metrics: ensure `METRICS_ENABLED=true` and the scraper targets port 8080 at `/metrics`.
