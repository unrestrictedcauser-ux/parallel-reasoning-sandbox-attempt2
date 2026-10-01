"""
PRSA — Plausible Reasoning & Synthesis Architecture
Core workflow prototype

Phases:
1. Ingestion & Preservation
2. Claim Decomposition
3. Objective Observation
4. Parallel Counter-Analysis
5. Synthesis & Decision
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


# ============================================================
# ENUMS
# ============================================================

class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    CORRELATED = "correlated"
    PLAUSIBLE = "plausible"
    UNKNOWN = "unknown"
    CONTRADICTED = "contradicted"


class SynthesisStatus(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INCONCLUSIVE = "inconclusive"
    INSUFFICIENT_DATA = "insufficient_data"
 

# ============================================================
# PHASE 1 — INGESTION & PRESERVATION
# ============================================================

@dataclass(frozen=True)
class Provenance:
    source: str
    timestamp: datetime
    context: Optional[str] = None


@dataclass(frozen=True)
class OriginalInput:
    """
    Immutable original input.

    Once created, the original text cannot be silently changed.
    """
    input_id: str
    raw_content: str
    provenance: Provenance


def ingest(
    raw_content: str,
    source: str,
    context: Optional[str] = None
) -> OriginalInput:

    if not raw_content.strip():
        raise ValueError("PRSA input cannot be empty.")

    return OriginalInput(
        input_id=str(uuid4()),
        raw_content=raw_content,
        provenance=Provenance(
            source=source,
            timestamp=datetime.now(timezone.utc),
            context=context,
        ),
    )


# ============================================================
# PHASE 2 — CLAIM DECOMPOSITION
# ============================================================

@dataclass
class Hypothesis:
    hypothesis_id: str
    statement: str

    # Explicit logical alternatives.
    ors: list[str] = field(default_factory=list)

    # Phase 3 material
    observations: list[str] = field(default_factory=list)
    missing_variables: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    # Phase 4 material
    falsification_conditions: list[str] = field(default_factory=list)

    status: EvidenceStatus = EvidenceStatus.UNKNOWN


def create_hypothesis(
    statement: str,
    ors: Optional[list[str]] = None
) -> Hypothesis:

    if not statement.strip():
        raise ValueError("Hypothesis statement cannot be empty.")

    return Hypothesis(
        hypothesis_id=str(uuid4()),
        statement=statement,
        ors=list(ors or []),
    )


# ============================================================
# PHASE 3 — OBJECTIVE OBSERVATION
# ============================================================

@dataclass(frozen=True)
class Observation:
    statement: str
    source: Optional[str] = None
    verifiable: bool = False


def add_observation(
    hypothesis: Hypothesis,
    statement: str,
    *,
    source: Optional[str] = None,
    verifiable: bool = False,
) -> Observation:

    observation = Observation(
        statement=statement,
        source=source,
        verifiable=verifiable,
    )

    hypothesis.observations.append(statement)

    return observation


def add_missing_variable(
    hypothesis: Hypothesis,
    variable: str
) -> None:
    """
    Missing information remains explicit.
    It is not silently converted into evidence.
    """
    hypothesis.missing_variables.append(variable)


def add_assumption(
    hypothesis: Hypothesis,
    assumption: str
) -> None:
    hypothesis.assumptions.append(assumption)


# ============================================================
# PHASE 4 — PARALLEL COUNTER-ANALYSIS
# ============================================================

@dataclass
class ReasoningBranch:
    branch_id: str
    hypothesis_id: str
    explanation: str

    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)

    assumptions: list[str] = field(default_factory=list)
    missing_variables: list[str] = field(default_factory=list)

    falsification_conditions: list[str] = field(default_factory=list)

    status: EvidenceStatus = EvidenceStatus.UNKNOWN


class ParallelSandbox:
    """
    Maintains competing explanations without allowing
    one branch to overwrite another.
    """

    def __init__(self):
        self.branches: dict[str, ReasoningBranch] = {}

    def create_branch(
        self,
        hypothesis: Hypothesis,
        explanation: str
    ) -> ReasoningBranch:

        branch = ReasoningBranch(
            branch_id=str(uuid4()),
            hypothesis_id=hypothesis.hypothesis_id,
            explanation=explanation,
        )

        self.branches[branch.branch_id] = branch
        return branch

    def add_support(
        self,
        branch_id: str,
        evidence: str
    ) -> None:
        self.branches[branch_id].supporting_evidence.append(evidence)

    def add_contradiction(
        self,
        branch_id: str,
        evidence: str
    ) -> None:
        self.branches[branch_id].contradicting_evidence.append(evidence)

    def add_falsifier(
        self,
        branch_id: str,
        condition: str
    ) -> None:
        self.branches[branch_id].falsification_conditions.append(condition)

    def set_status(
        self,
        branch_id: str,
        status: EvidenceStatus
    ) -> None:
        self.branches[branch_id].status = status


# ============================================================
# PHASE 5 — SYNTHESIS
# ============================================================

@dataclass(frozen=True)
class SynthesisResult:
    synthesis_id: str
    branch_results: dict[str, EvidenceStatus]
    unresolved_variables: list[str]
    correlation_warnings: list[str]
    status: SynthesisStatus
    summary: str

    # PRSA never turns synthesis into automatic execution.
    requires_human_decision: bool = True


def synthesize(
    sandbox: ParallelSandbox,
    *,
    unresolved_variables: Optional[list[str]] = None,
    correlation_warnings: Optional[list[str]] = None,
) -> SynthesisResult:

    if not sandbox.branches:
        raise ValueError(
            "PRSA cannot synthesize before parallel branches exist."
        )

    branch_results = {
        branch_id: branch.status
        for branch_id, branch in sandbox.branches.items()
    }

    statuses = list(branch_results.values())

    # Conservative synthesis:
    # uncertainty remains uncertainty.
    if all(
        status == EvidenceStatus.CONTRADICTED
        for status in statuses
    ):
        final_status = SynthesisStatus.CONTRADICTED
        summary = "All currently mapped branches are contradicted."

    elif (
        EvidenceStatus.UNKNOWN in statuses
        or EvidenceStatus.PLAUSIBLE in statuses
    ):
        final_status = SynthesisStatus.INCONCLUSIVE
        summary = (
            "Multiple possibilities remain unresolved. "
            "PRSA does not collapse them into a single conclusion."
        )

    elif EvidenceStatus.VERIFIED in statuses:
        final_status = SynthesisStatus.SUPPORTED
        summary = (
            "At least one branch contains verified support. "
            "Alternative branches remain preserved in the record."
        )

    else:
        final_status = SynthesisStatus.INSUFFICIENT_DATA
        summary = "Available evidence is insufficient for resolution."

    return SynthesisResult(
        synthesis_id=str(uuid4()),
        branch_results=branch_results,
        unresolved_variables=list(unresolved_variables or []),
        correlation_warnings=list(correlation_warnings or []),
        status=final_status,
        summary=summary,
        requires_human_decision=True,
    )


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    # Phase 1
    original = ingest(
        raw_content=(
            "The system failed shortly after "
            "the configuration changed."
        ),
        source="operator_report",
    )

    # Phase 2
    hypothesis = create_hypothesis(
        "The configuration change caused the failure.",
        ors=[
            "Infrastructure failure",
            "External dependency failure",
            "Coincidental timing",
        ],
    )

    # Phase 3
    add_observation(
        hypothesis,
        "The configuration change occurred before the failure.",
        verifiable=True,
    )

    add_missing_variable(
        hypothesis,
        "Exact failure start timestamp",
    )

    add_assumption(
        hypothesis,
        "The relevant configuration was active when failure began.",
    )

    # Phase 4
    sandbox = ParallelSandbox()

    config_branch = sandbox.create_branch(
        hypothesis,
        "The configuration change caused the failure.",
    )

    infrastructure_branch = sandbox.create_branch(
        hypothesis,
        "An independent infrastructure failure caused the failure.",
    )

    coincidence_branch = sandbox.create_branch(
        hypothesis,
        "The timing relationship was coincidental.",
    )

    sandbox.add_falsifier(
        config_branch.branch_id,
        "Logs prove the failure began before the configuration change.",
    )

    sandbox.set_status(
        config_branch.branch_id,
        EvidenceStatus.PLAUSIBLE,
    )

    sandbox.set_status(
        infrastructure_branch.branch_id,
        EvidenceStatus.UNKNOWN,
    )

    sandbox.set_status(
        coincidence_branch.branch_id,
        EvidenceStatus.UNKNOWN,
    )

    # Phase 5
    result = synthesize(
        sandbox,
        unresolved_variables=[
            "Exact failure start timestamp",
            "Infrastructure health records",
        ],
        correlation_warnings=[
            (
                "Configuration change preceded failure, "
                "but temporal ordering alone does not establish causation."
            )
        ],
    )

    print(result)