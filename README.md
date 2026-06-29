# Online Companion Package

Companion audit materials for **Functional Decentralization in Content Delivery Networks: A Responsibility-Plane Survey**.

This repository provides supporting audit materials for the manuscript. The paper is self-contained; these files make the cited-source metadata, review protocol, responsibility-plane profile, representative source-to-claim map, quantitative anchors, deployment landscape, and D0-D3 coding protocol inspectable.

## Fixed Snapshot

Manuscript companion URL:

```tex
\newcommand{\companionURL}{\url{https://github.com/ermalimust/dcdn-responsibility-plane-companion/tree/v1.0-submission}}
```

The `v1.0-submission` tag identifies the version used for manuscript submission.

## Contents

### Data

- `data/included_sources_metadata.csv`: metadata for the 208 cited sources in the manuscript bibliography, including citation-closure fields.
- `data/review_protocol_summary.csv`: compact summary of the review protocol, corpus accounting, and extraction logic reported in the manuscript.
- `data/claim_source_map_representative.csv`: representative source-to-claim map corresponding to the manuscript synthesis table.
- `data/responsibility_plane_profile.csv`: lower-bound D0-D3 responsibility-plane profile for the six architecture families and five planes.
- `data/quantitative_anchors.csv`: quantitative anchors used in the comparative discussion, with baselines, evidence type, and caveats.
- `data/deployment_landscape.csv`: deployed and industrial DCDN/Web3 delivery examples, reported evidence, and retained control boundaries.
- `data/candidate_records_summary.csv`: aggregate corpus counts reported in the manuscript.

### Reliability and Coding Protocol

- `reliability/coding_protocol.md`: D0-D3 code definitions, tie-break rules, and responsibility-plane questions.
- `reliability/reliability_summary.csv`: independent-coding reliability statistics reported in the manuscript.
- `reliability/final_lower_bound_profile.csv`: final lower-bound profile reported in the manuscript.
- `reliability/compute_kappa.py`: standard-library Python script used for ordinal agreement calculations.

### Bibliography Snapshot

- `bibliography/ref.bib`: BibTeX snapshot used for the manuscript.
- `bibliography/main.bbl`: compiled bibliography snapshot.

## Snapshot Summary

- Cited sources in bibliography: 208
- Citation closure check against `main.tex`: 208/208
- Submission tag: `v1.0-submission`
