# SCBE Nodal Network

This repository contains a reference implementation of a **multi‑agent nodal network** inspired by the principles of Sacred Covenant Bundle Engine (SCBE) and the Aethermoore architecture.  The goal is to provide a flexible toolkit for building hierarchical networks of agents that communicate, vote and reconstruct knowledge through bundles and offset mirrors.

## Features

* **Balanced ternary and signed binary logic** – represent agent beliefs and polarity using three‑valued and two‑valued enumerations.  This supports explicit expression of approval, neutrality and opposition, as well as pure support/attack dynamics.
* **Node abstraction** – a generic unit with semantic state, memory, confidence and connectivity.  Nodes can be arranged in parent/child trees and sibling meshes.
* **Bundles and offset bundles** – group nodes into bundles that operate together under different roles or tongues.  Offset bundles mirror a base bundle under a controlled perturbation (e.g. time shift or stricter governance) and allow for comparative analysis.
* **Coherence and stability metrics** – compute internal agreement among bundle members and measure how stable an interpretation remains under offsets.
* **Simple fusion strategies** – fuse ternary votes using majority vote or thresholding.  Offset bundles can combine their result with their base bundle to produce conservative decisions.

## Structure

The core implementation resides in the `scbe_nodal_network` package:

* `ternary.py` defines the `BalancedTernary` and `SignedBinary` enums, along with helper functions for summing and voting.
* `node.py` defines the `Node` class which holds semantic state, memory, confidence and connections.  Subclass `Node` to implement domain‑specific update logic.
* `bundle.py` defines the `Bundle` class, which groups nodes, computes coherence and fuses outputs, and the `OffsetBundle` subclass which mirrors a base bundle under an offset.  It also contains utility functions for fusing votes.
* `__init__.py` exposes the public API of the package.

## Example Usage

```python
from scbe_nodal_network import BalancedTernary, Node, Bundle

# Create a bundle with three nodes representing a simple decision
nodes = [Node(node_id=f"n{i}", role="agent") for i in range(3)]
bundle = Bundle(bundle_id="demo", nodes=nodes)

# Assign votes to each node (e.g. for safety)
votes = [BalancedTernary.POSITIVE, BalancedTernary.NEUTRAL, BalancedTernary.NEGATIVE]
for node, vote in zip(nodes, votes):
    node.semantic_state = [vote]

# Compute coherence and fused decision
print("Coherence:", bundle.compute_coherence())
print("Fused decision:", bundle.fuse_output())

# Create an offset bundle representing a stricter view
offset = OffsetBundle(bundle_id="demo_offset", base_bundle=bundle, offset_descriptor="strict")
for shadow_node in offset.nodes:
    # Force a stricter rule: if base vote was NEUTRAL, shadow interprets as NEGATIVE
    if shadow_node.semantic_state and shadow_node.semantic_state[0] is BalancedTernary.NEUTRAL:
        shadow_node.semantic_state[0] = BalancedTernary.NEGATIVE

print("Offset fused decision:", offset.fuse_output())
print("Stability relative to base:", offset.measure_stability())
```

The example shows how to build a simple bundle of nodes, assign ternary votes, compute the internal coherence and fuse the outputs.  It then constructs an offset bundle and compares its decision with the base bundle.

## Licence

This project is released under the MIT Licence.  See `LICENCE` for details.
