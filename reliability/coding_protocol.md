# D0-D3 Responsibility-Plane Coding Protocol

This file summarizes the coding protocol used for the responsibility-plane profile reported in the manuscript.

## Ordinal Codes

| Code | Responsibility Pattern | Lower-Bound Decision Criterion |
|---|---|---|
| D0 | Operator-centralized | One identifiable CDN provider, platform operator, or steering authority controls the plane's main decision, verification, settlement, or policy function. |
| D1 | Coordinator-mediated distribution | Multiple nodes, vendors, peers, or edge sites execute the function, but admission, ranking, fallback, accounting, revocation, or policy remains mediated by an identifiable coordinator. |
| D2 | Federated or protocol-mediated | Multiple administrative domains or participants make ordinary decisions under shared protocols, standards, registries, or verifiable interfaces; no single delivery provider fully determines routine operation. |
| D3 | Permissionless or trust-minimized | Participation, verification, settlement, or governance can proceed without a required trusted coordinator for that plane, usually through cryptographic evidence, open protocols, or on-chain rules. |

## Coding Rules

1. Code the changed CDN responsibility, not the technology label.
2. Code routine CDN-grade operation, not the most decentralized mode the technology could support in principle.
3. Record retained dependency cues such as admission, ranking, fallback, accounting, gateway mediation, revocation, or policy authority.
4. When evidence supports two adjacent codes, assign the lower code and record the retained dependency.
5. Separate storage, naming, provider discovery, and media delivery claims.
6. Use evidence maturity to bound the supported claim, not to raise or lower the responsibility code.

## Planes

| Plane | Question |
|---|---|
| Data | Who serves or moves content objects, chunks, or media segments? |
| Control | Who chooses request routing, placement, admission, or fallback? |
| Trust | Who verifies service claims, integrity, and contribution? |
| Economic | Who allocates rewards, penalties, settlement, or contractual value? |
| Governance/Policy | Who can authorize, revoke, moderate, update, or resolve disputes? |
