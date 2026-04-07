"""Definition of the core Node class for the SCBE nodal network.

Nodes are the basic units of computation in this library.  They hold
semantic state, memory and connectivity information which link them to
other nodes in a hierarchical tree or mesh.  Each node belongs to at
most one parent (forming a tree) and may have multiple children and
sibling references.  Nodes also have a ``role`` string which
conceptually describes their function (e.g. ``"parser"``, ``"verifier"``).

The ``Node`` class is intentionally generic and does not prescribe a
particular update rule.  Users can subclass ``Node`` and override
``update_state`` to implement domain‑specific behaviour.  The default
implementation simply keeps the state unchanged.

In addition to managing state, nodes track a confidence value and a
memory list.  The confidence is a floating‑point number in [0, 1]
representing how certain the node is about its current state.  Memory
can store arbitrary objects corresponding to past observations or
intermediate results; this structure is left flexible to accommodate
different application needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence

from .ternary import BalancedTernary


@dataclass
class Node:
    """A node in a SCBE nodal network.

    Parameters
    ----------
    node_id:
        A unique identifier for this node.  Can be any hashable type.
    role:
        A human‑readable label describing the node's semantic function.
    tongue:
        An optional label for the semantic tongue the node represents,
        such as ``"KO"``, ``"AV"`` or other domain‑specific roles.
    parent:
        A reference to the node's parent.  ``None`` if this node is a
        root.
    children:
        A list of child nodes.  Populated when creating a network.  Do
        not set this directly; use ``add_child``.
    siblings:
        A list of nodes at the same depth that share the same parent.
    semantic_state:
        A sequence of ternary values representing the node's current
        interpretation across one or more features.  The meaning of
        each dimension depends on the domain.  Initially empty; can
        be populated by the user or during update.
    confidence:
        A float in [0, 1] indicating the node's confidence in its
        semantic state.
    memory:
        A list storing arbitrary past observations or intermediate
        computations.  This is opaque to the library.

    Notes
    -----
    ``update_state`` is a hook that subclasses can override to update
    ``semantic_state`` based on input and influence from neighbours.
    The base class leaves the state unchanged.
    """

    node_id: Any
    role: str = "generic"
    tongue: Optional[str] = None
    parent: Optional["Node"] = None
    children: List["Node"] = field(default_factory=list)
    siblings: List["Node"] = field(default_factory=list)
    semantic_state: Sequence[BalancedTernary] = field(default_factory=list)
    confidence: float = 0.0
    memory: List[Any] = field(default_factory=list)

    def add_child(self, child: "Node") -> None:
        """Attach a child node to this node.

        The child's parent will be set to this node and the child will
        be added to this node's list of children.  Sibling references
        are also updated among the existing children.

        Parameters
        ----------
        child:
            The node to add as a child.
        """
        child.parent = self
        # update sibling references for existing children
        for existing in self.children:
            existing.siblings.append(child)
            child.siblings.append(existing)
        self.children.append(child)

    def update_state(self, input_data: Any, neighbour_states: List[Sequence[BalancedTernary]]) -> None:
        """Update this node's semantic state.

        By default this method simply leaves ``semantic_state`` unchanged.
        Subclasses can override it to implement specific update logic.

        Parameters
        ----------
        input_data:
            Domain‑specific input provided to the node for interpretation.
        neighbour_states:
            A list of semantic state vectors from neighbouring nodes
            (parent, children, siblings) that can influence this node's
            update.  The base implementation ignores this parameter.
        """
        # Default behaviour: no update.  Override in subclasses.
        return

    def __repr__(self) -> str:
        return (f"Node(id={self.node_id!r}, role={self.role!r}, tongue={self.tongue!r},"
                f" state={[int(v) for v in self.semantic_state]}, confidence={self.confidence:.2f})")
