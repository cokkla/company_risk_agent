from dataclasses import dataclass, field


@dataclass
class ParsedResult:
    markdown: str
    status: str  # "success" | "partial_success" | "failed"
    parser_used: str
    warnings: list[str] = field(default_factory=list)
    page_errors: list[dict] = field(default_factory=list)


class ParseError(Exception):
    pass
