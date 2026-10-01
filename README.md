# Learn OpenTelemetry with Kubernetes and Buildkite

Start with the [step-by-step tutorial](tutorial/README.md). Learn the data flow, then collect job traces and logs, agent metrics, and Kubernetes telemetry. Each stage includes a checkpoint and an experiment.

The files in `tutorial/` are learning examples to deploy yourself, one stage at a time. The existing `opentelemetry-demo.yaml` is a separate, larger example used for an optional backend exercise.

## Before you start

- Begin with the small tutorial setup. The full demo's regular containers request roughly **8.86 GiB** of memory before Kubernetes system workloads and the tutorial resources. See [Rancher Desktop memory and scheduling](tutorial/README.md#rancher-desktop-memory-and-scheduling).
- Create the self-hosted Buildkite queue `otel-lab` in the cluster associated with your agent token. The agent tag selects that queue; it does not create it.
- The token Secret is `buildkite-agent-token` in namespace `buildkite`, with a field named `BUILDKITE_AGENT_TOKEN`. The manifest must match both names.
- The working token workflow uses your existing Bash variable `BUILDKITE_AGENT_TOKEN` from `~/.bash_profile`. Load it if needed, patch the Kubernetes Secret from the variable, then restart the agent. Follow [the token update steps](tutorial/README.md#change-the-agents-buildkite-cluster). The token must belong to the intended Buildkite cluster.
- The agent image is verified v3.137.2, pinned by digest. Its tracing settings use the v3 flag names documented in the tutorial.

## Understand the two agent setups

| Deployment | Role | Used in the tutorial |
| --- | --- | --- |
| `buildkite-agent` | A persistent agent that runs jobs in its own pod | Initial exercises |
| `agent-stack-k8s` | A controller that creates separate Kubernetes job pods | Later Agent Stack exercises |

If both pods appear, they belong to different Deployments; the controller is not an old standalone agent pod. See [choosing which setup to run](tutorial/README.md#choose-which-agent-setup-to-run) for commands to inspect ownership, pause the controller, and restore it later.

For startup failures, follow [the troubleshooting section](tutorial/README.md#12-troubleshoot-by-following-the-data): pod events explain scheduling/image/Secret errors, and previous-container logs explain crash loops.
