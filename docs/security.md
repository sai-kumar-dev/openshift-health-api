# Threat model

Assets are service availability, dependency credentials, operational metadata,
and trustworthy logs/metrics. Trust boundaries exist at the public Route,
request headers, environment/Secret injection, dependency network, container,
and image supply chain.

Likely threats include request-ID log injection, path-driven metric cardinality,
health-check denial of service, credential leakage, privileged containers,
mutable images, and compromised dependencies. Controls include strict request-ID
syntax, route-template labels, concurrent short timeouts, generic public check
details, non-root/read-only execution, dropped capabilities, no service-account
token, pinned Python dependencies, audit/scanning CI, and no secrets in manifests.

Known limitations: OpenAPI is enabled, host filtering/rate limiting is expected
at the ingress, dependency checks are TCP-level, the sample NetworkPolicy permits
all egress, CI actions use stable tags rather than immutable SHAs, and the sample
production image tag must be replaced with a digest for a real deployment.
