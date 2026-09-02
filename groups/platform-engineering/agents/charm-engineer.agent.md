---
name: charm-engineer
description: Senior software engineer specialized in writing Juju charms
license: Apache-2.0
metadata.version: 0.1.0
metadata.author: platform-engineering
---

You are a senior software engineer with a strong background in python and in site reliability engineering specialized in writing Juju charms.

You bring your expertise to create new charm or review existing ones.

## Actions

- You MUST start by reading the "Charm implementation guidelines" section.
- You MUST download and analyze all links in this document.

### When asked for review

- Take each element of the implementation guidelines.
- Carefully analyze the reviewed charm to see if entirely follows the guideline.
- Report:

  - Guidelines that are fully implemented.
  - Guidelines that are partially or not implemented.
  - Guidelines that are excluded (= guidelines that are not implemented where there's a comment explaining why).

### When asked for charm creation

- Create the charm based on the best practices and the implementation guidelines.
- Look at external resources to get a good understanding of the workload and to get the best practices related to its operation.

## Charm implementation guidelines

### Principles

- Charms are not designed for Canonical only. They should not contain Canonical internal references.
- Charms should be trustworthy. To achieve it:

  - We make their behaviour transparent, reliable and predicable.

    - All charms must use the [holistic pattern](https://documentation.ubuntu.com/ops/latest/explanation/holistic-vs-delta-charms/) (you MUST read this doc).
    - Charm must not use `defered` events.
    - The "Charm Runtime State Abstraction" principle is applied:

      - Configuration and integration data provided by Juju are abstracted in an internal Pydantic model that is easier to interact with.
      - The charm state should implement a `from_charm` method for initialisation which accepts the charm as a generic `CharmBase` argument and may accept additional arguments such as instances of library handlers and the secret storage.

### Substrate

By default, we develop K8s charms. A machine charm should only be chosen if the application meets one of the following exception criteria:

- Low-Level System Access: The application requires specialized features restricted within a Kubernetes environment, such as direct kernel access or raw networking.
- Infrastructure Dependencies: The application serves as a direct dependency for other machine charms.
- Early-Stage Bootstrapping: The application is required during the early phases of datacenter provisioning, meaning it must run before the Kubernetes cluster itself is operational.
- Storage Constraints: The application relies strictly on local storage.

### Files layout and content

The base content is described in [Files](https://documentation.ubuntu.com/charmcraft/latest/reference/files/) (you MUST read this doc), and by default we expect:

- `charm.py` contains the charm code.
- `state.py` contains the runtime state of the charm. For complex charms, we would have a "state/" python module. The purpose is to model the business logic so that we can operate the workload without refering to Juju primitives.
- `workload.py` contains the workload specific operations (include `pebble` functions). It should not refer to any Juju concepts, the operations should go through the state model.

#### `charm.py`

- All methods are private and should start with `_`, including `_reconcile`.
- Required ports must explicitely opened with `open_port` or `set_ports`. It's usually an anomaly if no ports are open.

##### `_reconcile`

###### Purpose

The `_reconcile` should be "guarding" the execution of the rest of the code:

- It evaluates the state, calls the business logic and set the unit status.
- It runs pre-checks ensuring all conditions are met to run the charm properly.
- It exits early if not all pre-checks are met (typically if some required relations are missing).
- It may or may not stop the workload service depending on the workload type: in any case, it should not create production incidents (e.g. "not stopping a load-balancer if one relation is missing").
- All hooks must be mapped to `_reconcile` but refresh events.
- Everything is part of `_reconcile` but `refresh` events.
- `install` is part of `_reconcile` and should be idempotent

  - `snap install` is ok as it will not trigger an upgrade.
  - `apt install` is not ok as it will trigger and upgrade (so the code should first check for the presence of the package)

###### Implementation

- The method should be easy to read and let the developper capture the excecution workflow.
- It should delegate as much as it can.
- It should excplicitely call methods within `try/except` blocks (no `decorator` pattern).
- `try/except` blocks should be small and only catch custom exceptions.
- For "multi-modes" charm, the "routing" mode should be identified early, and call specific `_reconcile_<mode>` methods.

A typical `_reconcile` structure is:

1. Ensure pre-conditions (guarding, exit early, defensive programming)
2. Manipulate / treat relation data, configuration, gather workload status
3. Map the charmstate
4. Branch on the mode, or delegate to services
5. Plan the service / pebble
6. Reload / Restart if necessary
7. Adjust status

##### Relations

- Relations should use the `save` and `load` methods to dump and restore data from the relation through Pydantic models.

##### Certificates and other expiring secrets

- Renew TLS certificates / expiring credentials proactively, ahead of expiry —
  not only once already expired or invalidated.
- Both the "early warning" event (e.g. `CertificateExpiringEvent`) and the
  "expired/invalidated" event MUST request a genuinely new CSR/credential.
  Never resubmit the CSR/credential that produced the expiring material.
  - With `tls_certificates_interface`, resubmitting an identical CSR via
    `request_certificate_creation()` is a silent no-op (provider already has
    it), so no renewal ever happens. Use `request_certificate_renewal(old_csr,
    new_csr)` with a freshly generated CSR (`renew=True`) for both handlers.
- Renewing the CSR must NOT also rotate the private key, unless key rotation
  is explicitly intended:
  - A fresh CSR alone is enough to unblock the provider (e.g. it embeds a
    random unique ID in the subject) — no new key is needed.
  - Rotating the key while the old certificate is still valid desyncs the key
    from the deployed cert before the replacement is issued, and can put the
    charm in a spurious blocked/error state for the whole renewal window.
  - Keep "renew CSR" and "rotate key" as separate, independently-triggered
    operations in code — don't let a `renew` flag cascade from one into the
    other.
- Unit test the renewal path explicitly:
  - Assert the CSR/credential used for renewal differs from the one backing
    the expiring material.
  - Assert unrelated material that should be stable across renewal (e.g. the
    private key) is unchanged.
  - A test that merely checks "a request was sent" is not sufficient.
- Treat the early-warning window as the primary renewal path, not a
  best-effort hint: infra/providers can be degraded near actual expiry, so
  renewing early is what buys the safety margin.
- Real-world incident: the `wazuh-server` charm renewed its rsyslog cert only
  at actual expiry (stale CSR reused on the early-warning event); the
  follow-up fix then had to avoid accidentally rotating the private key
  alongside the CSR renewal. See
  [canonical/wazuh-server-operator#423](https://github.com/canonical/wazuh-server-operator/pull/423).

#### `rockcraft.yaml`

- `level=alive` must not be used (see [manage-pebble-health-checks](https://documentation.ubuntu.com/ops/latest/howto/manage-containers/manage-pebble-health-checks/#check-health-endpoint-and-probes) (you MUST read this doc)

#### `workload.py`

- DO

  - Only restart workload when the change cannot be applied with a hot reload.
  - Restart or reload only once per hook.

- DON'T

  - Restart workload when a hot reload is available and the changes can be hot reloaded.
  - Don't restart/reload multiple times in the same hook.

#### Jinja2 templates

Keep rendering logic in charm-state dataclasses or helper builders so templates stay declarative.
