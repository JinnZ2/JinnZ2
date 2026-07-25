# claim_lineage.py
# CC0. stdlib-only. phone-buildable.
#
# The lineage graph for falsifiable claims. A claim is a node in a DAG:
# it has a statement, a prediction, and an explicit falsifier. Refinements
# and supersessions are edges, not mutations -- the old node stays.
#
# frontier() returns claims with no successors: the current leading edge.
# ancestors() returns the chain of prior versions, oldest first.
#
# No verdict fields. No implicit now(). Append-only: a superseded claim
# is kept; only the frontier moves. Same discipline as divlog.py.

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Claim:
    cid: str
    statement: str
    variables: tuple               # which variables the claim is over
    prediction: str                # what this claim says will happen
    refuted_if: str                # the observation that kills it
    parent: Optional[str] = None   # cid this refines or extends
    supersedes: Optional[str] = None  # cid this replaces (old stays in graph)
    as_of: str = ""
    notes: str = ""


class Lineage:
    """DAG of falsifiable claims. Nodes are never removed."""

    def __init__(self):
        self._claims: dict[str, Claim] = {}
        self._children: dict[str, list] = {}   # cid -> [child cids]

    def add_root(self, claim: Claim) -> Claim:
        """Add a claim with no parent. Returns the claim."""
        self._claims[claim.cid] = claim
        return claim

    def refine(self, parent_cid: str, child: Claim) -> Claim:
        """Add a claim that specialises or extends an existing one."""
        if parent_cid not in self._claims:
            raise KeyError(f"parent '{parent_cid}' not in lineage")
        child.parent = parent_cid
        self._claims[child.cid] = child
        self._children.setdefault(parent_cid, []).append(child.cid)
        return child

    def supersede(self, old_cid: str, new_claim: Claim) -> Claim:
        """Add a replacement. Old node stays; frontier moves to new_claim."""
        if old_cid not in self._claims:
            raise KeyError(f"'{old_cid}' not in lineage")
        new_claim.supersedes = old_cid
        self._claims[new_claim.cid] = new_claim
        self._children.setdefault(old_cid, []).append(new_claim.cid)
        return new_claim

    def frontier(self) -> List[Claim]:
        """Claims with no successors -- the current leading edge."""
        has_children = set(self._children)
        return [c for c in self._claims.values() if c.cid not in has_children]

    def ancestors(self, cid: str) -> List[Claim]:
        """Chain of prior versions, oldest first, ending just before cid."""
        claim = self._claims.get(cid)
        if claim is None:
            return []
        chain: List[Claim] = []
        visited = {cid}
        cur = claim
        while cur.parent or cur.supersedes:
            prior_cid = cur.supersedes or cur.parent
            if prior_cid in visited or prior_cid not in self._claims:
                break
            visited.add(prior_cid)
            prior = self._claims[prior_cid]
            chain.append(prior)
            cur = prior
        chain.reverse()
        return chain

    def get(self, cid: str) -> Optional[Claim]:
        return self._claims.get(cid)

    def all_claims(self) -> List[Claim]:
        return list(self._claims.values())
