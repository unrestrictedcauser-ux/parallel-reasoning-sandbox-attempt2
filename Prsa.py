"""
PRSA v0.1
Plausible Reasoning & Synthesis Architecture

Core rule:
Competing interpretations are preserved independently before synthesis.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Claim:
    """A claim being examined by PRSA."""

    statement: str
    supporting_evidence: List[str] = field(default_factory=list)
    opposing_evidence: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)


@dataclass
class Analysis:
    """Independent analysis of one claim."""

    claim: Claim
    plausible_interpretations: List[str] = field(default_factory=list)
    counter_interpretations: List[str] = field(default_factory=list)


def analyze_claim(claim: Claim) -> Analysis:
    """
    Preserve competing interpretations without deciding between them.

    Synthesis is deliberately excluded from this stage.
    """

    analysis = Analysis(claim=claim)

    if claim.supporting_evidence:
        analysis.plausible_interpretations.append(
            "The available supporting evidence is consistent with the claim."
        )

    if claim.opposing_evidence:
        analysis.counter_interpretations.append(
            "The available opposing evidence provides an alternative interpretation."
        )

    if claim.unknowns:
        analysis.counter_interpretations.append(
            "Unresolved information prevents a definitive conclusion."
        )

    return analysis


def synthesize(analysis: Analysis) -> dict:
    """
    Synthesis occurs only after competing interpretations
    have been independently preserved.
    """

    return {
        "claim": analysis.claim.statement,
        "supporting_evidence": analysis.claim.supporting_evidence,
        "opposing_evidence": analysis.claim.opposing_evidence,
        "unknowns": analysis.claim.unknowns,
        "plausible_interpretations": analysis.plausible_interpretations,
        "counter_interpretations": analysis.counter_interpretations,
    }


if __name__ == "__main__":
    example = Claim(
        statement="Example claim",
        supporting_evidence=[],
        opposing_evidence=[],
        unknowns=["Additional evidence is required."],
    )

    result = synthesize(analyze_claim(example))
    print(result)
