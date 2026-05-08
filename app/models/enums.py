from enum import StrEnum


class Visibility(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class PullRequestStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    REJECTED = "REJECTED"
    MERGED = "MERGED"


class ContributionGrade(StrEnum):
    MAJOR = "MAJOR"
    NORMAL = "NORMAL"
    MINOR = "MINOR"


class ConflictRiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RejectCategory(StrEnum):
    CONFLICT = "CONFLICT"
    TOO_VAGUE = "TOO_VAGUE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    MISALIGNED = "MISALIGNED"
    DUPLICATE = "DUPLICATE"
    INAPPROPRIATE = "INAPPROPRIATE"
    OTHER = "OTHER"
