# Banxico Connectors Documentation

This documentation is organized around the MainSequence concepts used by the
project: DataNodes, market objects, instruments, and dashboards.

## Pages

- [Introduction](introduction.md)
- [Deployment And CLI](deployment.md)
- [DataNodes](data-nodes.md)
- [Markets](markets.md)
- [Instruments](instruments.md)
- [Dashboards](dashboards.md)

## Scope

The current repository focuses on Banxico SIE ingestion for Mexican rates,
publishing reference-rate fixings into MainSequence, and building a Banxico MXN
zero curve from on-the-run market instruments.

The docs also distinguish clearly between:

- what is implemented in the repository,
- what the current MainSequence CLI expects,
- and what a healthy deployed state should look like after sync, image build,
  batch job submission, and successful runs.
