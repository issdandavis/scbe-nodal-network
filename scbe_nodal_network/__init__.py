"""Top‑level package for the SCBE nodal network library.

This package implements an abstract multi‑agent architecture inspired by
Sacred Covenant Bundle Engine (SCBE) and Aethermoore design principles.
It provides a set of primitives for constructing trees of cooperating
agents, including binary and ternary nodes, sibling meshes, bundles,
offset mirrors and simple reconstruction functions.

The design exposed here is deliberately lightweight and compositional.
It offers base classes which can be extended to implement concrete
behaviours and governance logic.  Out of the box it supports the
following concepts:

* ``BalancedTernary`` – a three‑valued enumeration representing positive,
  neutral (witness) and negative semantics.  This is more expressive
  than Boolean logic and allows nodes to explicitly defer judgment.
* ``SignedBinary`` – a two‑valued enumeration with polarity.  It is
  useful for modelling simple adversarial/support relations and
  alternating force fields.
* ``Node`` – a generic unit of computation with references to parent,
  children and siblings.  Nodes hold semantic state, memory and a
  confidence score and provide hooks for updating state based on inputs
  and neighbour influence.
* ``Bundle`` – a collection of nodes which collectively interpret an
  input under different roles or tongues.  Bundles compute internal
  coherence and can fuse outputs from their constituent nodes into a
  single ternary or binary decision.
* ``OffsetBundle`` – a specialised bundle which holds a reference to a
  base bundle and applies an offset in time, memory or policy.  Offset
  bundles are used to compare how interpretations change under
  perturbations.

The package also exposes helper functions for fusing ternary votes,
computing coherence and measuring stability across bundles.  These
utilities can be composed to build larger tree‑of‑bundles structures
with nested governance layers.

Example usage::

    from scbe_nodal_network import BalancedTernary, Node, Bundle

    # Create a simple bundle of three nodes which each vote on a
    # hypothetical safety property.
    nodes = [Node(node_id=f"n{i}", role="safety") for i in range(3)]
    bundle = Bundle(bundle_id="safety_bundle", nodes=nodes)
    votes = [BalancedTernary.POSITIVE, BalancedTernary.NEUTRAL, BalancedTernary.NEGATIVE]
    for node, vote in zip(nodes, votes):
        node.semantic_state = [vote]  # simple 1‑D vector

    fused = bundle.fuse_output()
    assert fused == BalancedTernary.NEUTRAL

Note that this package does not implement any particular domain logic
itself.  It is intended to form a foundation upon which to build
specialised SCBE‑compliant systems.

"""

from .ternary import BalancedTernary, SignedBinary
from .node import Node
from .bundle import Bundle, OffsetBundle, fuse_ternary_votes

__all__ = [
    "BalancedTernary",
    "SignedBinary",
    "Node",
    "Bundle",
    "OffsetBundle",
    "fuse_ternary_votes",
]
