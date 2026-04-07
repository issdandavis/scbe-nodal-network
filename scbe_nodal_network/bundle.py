"""Definition of bundle structures for the SCBE nodal network.

Bundles are groups of nodes which collectively interpret inputs and
produce a fused output.  They capture the idea of a symbiotic
micro ecosystem of specialised agents, such as the six Sacred Tongues
in SCBE.  A bundle aggregates the semantic state of its constituent
nodes and computes measures such as coherence (degree of agreement)
and stability across offset mirrors.  Bundles can also produce a
fused ternary decision via majority voting or weighted aggregation.

An ``OffsetBundle`` is a wrapper around another bundle that introduces
a controlled perturbation (e.g. time shift, stricter policy, memory
compression).  Offset bundles allow the system to compare how
interpretations change when viewed under different perspectives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

from .node import Node
from .ternary import BalancedTernary, majority_vote, balanced_ternary_sum



def fuse_ternary_votes(votes: Sequence[BalancedTernary], threshold: Optional[int] = None) -> BalancedTernary:
    """Fuse a sequence of ternary votes into a single decision.

    The fusion works by summing the integer codes of each vote and
    thresholding the result.  If the sum is greater than a positive
    threshold, the result is ``POSITIVE``; if less than the negative
    threshold, the result is ``NEGATIVE``.  Otherwise the result is
    ``NEUTRAL``.  When ``threshold`` is ``None``, the default
    threshold of half the number of votes is used.

    Parameters
    ----------
    votes:
        A sequence of :class:`BalancedTernary` values.
    threshold:
        An optional integer specifying the absolute threshold for
        deciding a positive or negative result.  If ``None``, uses
        ``len(votes) // 2 + 1`` (more than half the votes) as the
        threshold.

    Returns
    -------
    BalancedTernary
        The fused ternary decision.
    """
    if not votes:
        return BalancedTernary.NEUTRAL
    if threshold is None:
        threshold = len(votes) // 2 + 1
    total = balanced_ternary_sum(list(votes))
    if total >= threshold:
        return BalancedTernary.POSITIVE
    elif total <= -threshold:
        return BalancedTernary.NEGATIVE
    else:
        return BalancedTernary.NEUTRAL


@dataclass
class Bundle:
    """A collection of nodes that collectively interpret an input.

    A bundle encapsulates a set of nodes that operate together.  Each
    node may have a different role or tongue, but the bundle as a whole
    can compute aggregate measures such as coherence and can fuse the
    individual votes into a single ternary decision.  Bundles are
    typically arranged in a larger tree structure, with offset mirror
    bundles providing alternative perspectives.

    Parameters
    ----------
    bundle_id:
        A unique identifier for this bundle.
    nodes:
        The nodes comprising this bundle.
    offset_descriptor:
        A human readable description of how this bundle differs from
        its base bundle when used as an offset mirror (e.g.
        ``"future+1"``, ``"strict_policy"``).  ``None`` for base
        bundles.
    base_bundle:
        A reference to the bundle that this offset mirror is derived
        from.  ``None`` if this is a base bundle.
    """

    bundle_id: str
    nodes: List[Node] = field(default_factory=list)
    offset_descriptor: Optional[str] = None
    base_bundle: Optional["Bundle"] = None

    def add_node(self, node: Node) -> None:
        """Add a node to this bundle.

        The node is appended to the list of nodes.  This does not
        update any hierarchical relations; it is simply a container
        operation.
        """
        self.nodes.append(node)

    def compute_coherence(self) -> float:
        """Compute the internal coherence of the bundle.

        Coherence is defined as the fraction of pairwise state
        agreements among the nodes in the bundle.  For each feature
        dimension, if two nodes have the same ternary value, their
        agreement on that feature contributes 1; a disagreement
        contributes 0; and one neutral and one non neutral value
        contributes 0.5.  The final coherence is the average over
        all pairs and features.

        Returns
        -------
        float
            A coherence score between 0 and 1.  1 indicates perfect
            agreement, 0 indicates complete disagreement.
        """
        if len(self.nodes) < 2:
            return 1.0  # trivially coherent
        total_pairs = 0
        total_agreement = 0.0
        # compute pairwise agreement for each feature
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                n1 = self.nodes[i]
                n2 = self.nodes[j]
                if not n1.semantic_state or not n2.semantic_state:
                    continue  # skip if no state defined
                assert len(n1.semantic_state) == len(n2.semantic_state), (
                    "All nodes in a bundle must have semantic_state of the same length"
                )
                for a, b in zip(n1.semantic_state, n2.semantic_state):
                    total_pairs += 1
                    if a == b:
                        total_agreement += 1.0
                    elif BalancedTernary.NEUTRAL in (a, b):
                        total_agreement += 0.5
                    else:
                        total_agreement += 0.0
        if total_pairs == 0:
            return 1.0
        return total_agreement / total_pairs

    def fuse_output(self, threshold: Optional[int] = None) -> BalancedTernary:
        """Fuse the nodes' outputs into a single ternary decision.

        By default this uses the :func:`fuse_ternary_votes` helper.
        Subclasses can override this method to implement alternative
        fusion strategies, such as majority voting, weighted sums or
        harmonic governance rules.  The optional ``threshold`` can be
        supplied to adjust how many votes are required for a positive or
        negative result.

        Parameters
        ----------
        threshold:
            Optional threshold for the fusion.  See
            :func:`fuse_ternary_votes` for details.

        Returns
        -------
        BalancedTernary
            The fused decision representing the collective judgment of
            this bundle.
        """
        votes = []
        for node in self.nodes:
            # treat an empty semantic state as NEUTRAL
            if not node.semantic_state:
                votes.append(BalancedTernary.NEUTRAL)
            else:
                # simple strategy: use the first dimension as the vote
                votes.append(node.semantic_state[0])
        return fuse_ternary_votes(votes, threshold=threshold)

    def measure_stability(self) -> Optional[float]:
        """Measure this bundle's stability relative to its base.

        Stability is defined only for offset bundles.  It computes the
        proportion of semantic dimensions that remain identical between
        this bundle and its base bundle across all constituent nodes.
        If this bundle is not an offset, returns ``None``.

        Returns
        -------
        Optional[float]
            A stability score in [0, 1] if the bundle has a base
            bundle; ``None`` otherwise.
        """
        if self.base_bundle is None:
            return None
        if len(self.nodes) != len(self.base_bundle.nodes):
            raise ValueError("Offset bundle and base bundle must have the same number of nodes")
        total = 0
        unchanged = 0
        for n_off, n_base in zip(self.nodes, self.base_bundle.nodes):
            if not n_off.semantic_state or not n_base.semantic_state:
                continue
            assert len(n_off.semantic_state) == len(n_base.semantic_state)
            for a, b in zip(n_off.semantic_state, n_base.semantic_state):
                total += 1
                if a == b:
                    unchanged += 1
        if total == 0:
            return 1.0
        return unchanged / total


class OffsetBundle(Bundle):
    """A bundle that applies an offset relative to a base bundle.

    Offset bundles are created from a base bundle and typically apply
    controlled perturbations such as time shifts, role shifts or
    stricter governance.  They mirror the structure of the base bundle
    (same number of nodes) but may differ in their semantic states.  The
    ``offset_descriptor`` describes the nature of the perturbation and
    can be used for diagnostic or logging purposes.
    """

    def __init__(self, bundle_id: str, base_bundle: Bundle, offset_descriptor: str):
        super().__init__(bundle_id=bundle_id, nodes=[], offset_descriptor=offset_descriptor, base_bundle=base_bundle)
        # create shadow nodes corresponding to each node in the base bundle
        for base_node in base_bundle.nodes:
            shadow = Node(
                node_id=f"{base_node.node_id}_offset_{offset_descriptor}",
                role=base_node.role,
                tongue=base_node.tongue,
                parent=None,
                children=[],
                siblings=[],
                semantic_state=list(base_node.semantic_state),
                confidence=base_node.confidence,
                memory=list(base_node.memory),
            )
            self.nodes.append(shadow)

    def fuse_output(self, threshold: Optional[int] = None) -> BalancedTernary:
        """Override fusion to consider both this and base bundle.

        This method fuses the outputs of the offset bundle and its base
        bundle together.  It returns ``NEGATIVE`` if either bundle
        produces a negative result, ``POSITIVE`` if both produce a
        positive result, and ``NEUTRAL`` otherwise.  This is a simple
        conservative rule; subclasses can implement more sophisticated
        strategies.
        """
        if self.base_bundle is None:
            return super().fuse_output(threshold=threshold)
        base_vote = self.base_bundle.fuse_output(threshold=threshold)
        offset_vote = super().fuse_output(threshold=threshold)
        if base_vote is BalancedTernary.NEGATIVE or offset_vote is BalancedTernary.NEGATIVE:
            return BalancedTernary.NEGATIVE
        if base_vote is BalancedTernary.POSITIVE and offset_vote is BalancedTernary.POSITIVE:
            return BalancedTernary.POSITIVE
        return BalancedTernary.NEUTRAL
