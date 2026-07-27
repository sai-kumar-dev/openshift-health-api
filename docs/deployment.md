# Deployment

The base contains common Deployment, Service, Route, ServiceAccount,
ConfigMap, and ingress policy. Development remains single-replica. Production
adds three replicas, an HPA (3–6), a PDB requiring two available pods, and
best-effort topology spread.

Run `kubectl kustomize deploy/overlays/development` and the production equivalent
before `oc apply -k`. Provide dependency URLs through OpenShift Secrets and
`secretKeyRef` patches; never add them to the generated ConfigMap. The pod uses
an `emptyDir` at `/tmp`, allowing a read-only root filesystem and arbitrary UID.
Validate rollout, probes, Route TLS, logs, metrics, security context, and cleanup
on the target cluster.
