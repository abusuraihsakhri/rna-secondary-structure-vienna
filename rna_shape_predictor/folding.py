"""Validated ViennaRNA minimum-free-energy folding (optional native dependency)."""

MAX_SEQUENCE_LENGTH = 500


class FoldingUnavailableError(RuntimeError):
    """The ViennaRNA native Python bindings are not installed."""


def normalize_sequence(raw: str) -> str:
    """Accept one plain RNA sequence or FASTA entry; normalize DNA T to RNA U."""
    if not isinstance(raw, str):
        raise ValueError("Sequence must be text")
    lines = raw.strip().splitlines()
    if lines and lines[0].strip().startswith(">"):
        lines.pop(0)
    if any(line.strip().startswith(">") for line in lines):
        raise ValueError("Provide only one FASTA sequence")
    sequence = "".join("".join(lines).split()).upper().replace("T", "U")
    if not sequence:
        raise ValueError("Sequence must not be empty")
    if len(sequence) > MAX_SEQUENCE_LENGTH:
        raise ValueError(f"Sequence exceeds {MAX_SEQUENCE_LENGTH} nucleotides")
    if any(base not in "ACGU" for base in sequence):
        raise ValueError("Only A, C, G, U (or DNA T normalized to U) are supported")
    return sequence


def parse_dot_bracket(structure: str) -> list[list[int]]:
    """Return 1-indexed base pairs; reject invalid or unbalanced notation."""
    stack: list[int] = []
    pairs: list[list[int]] = []
    for idx, char in enumerate(structure, start=1):
        if char == "(":
            stack.append(idx)
        elif char == ")":
            if not stack:
                raise ValueError("Unbalanced dot-bracket structure")
            pairs.append([stack.pop(), idx])
        elif char != ".":
            raise ValueError("Invalid dot-bracket character")
    if stack:
        raise ValueError("Unbalanced dot-bracket structure")
    return sorted(pairs)


def fold_rna(raw: str) -> dict:
    """Compute true MFE with official ViennaRNA/RNAlib Python bindings."""
    sequence = normalize_sequence(raw)
    try:
        import RNA  # type: ignore[import-not-found]
    except ImportError as exc:
        raise FoldingUnavailableError("ViennaRNA is unavailable; install with pip install '.[vienna]'") from exc
    structure, energy = RNA.fold(sequence)
    if len(structure) != len(sequence):
        raise RuntimeError("ViennaRNA returned a structure of unexpected length")
    pairs = parse_dot_bracket(structure)
    return {
        "sequence": sequence,
        "structure": structure,
        "energy_kcal_mol": float(energy),
        "length": len(sequence),
        "base_pairs": pairs,
        "gc_percent": round(100 * sum(c in "GC" for c in sequence) / len(sequence), 2),
        "method": "ViennaRNA RNA.fold minimum free energy (default model)",
    }
