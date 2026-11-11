"""Execute the complete reproducible BER sweep and write raw results."""

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from sim import channel, line_codes, modulation
from sim.link import run_link
from sim.source import load_source

EBN0_VALUES = list(range(0, 21, 2))
SEEDS = list(range(5))
RESULTS = Path("results")
RAW_CSV = RESULTS / "raw.csv"
RUN_INFO = RESULTS / "run_info.json"


def _git_metadata() -> tuple[str | None, bool | None]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL
            ).strip()
        )
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, None


def _implementation_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in sorted(Path("src/sim").glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    text = load_source()
    fieldnames = [
        "line_code",
        "modulation",
        "scenario",
        "ebn0_db",
        "seed",
        "n_bits",
        "bit_errors",
        "ber",
        "violations",
        "spectral_efficiency",
    ]
    total = len(line_codes.NAMES) * len(modulation.NAMES) * len(channel.SCENARIOS)
    combination = 0
    with RAW_CSV.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for scenario in channel.SCENARIOS:
            for line_code in line_codes.NAMES:
                for modulation_name in modulation.NAMES:
                    combination += 1
                    print(
                        f"[{combination:02d}/{total}] {scenario} / {line_code} / {modulation_name}",
                        flush=True,
                    )
                    for ebn0_db in EBN0_VALUES:
                        for seed in SEEDS:
                            result = run_link(
                                text, line_code, modulation_name, scenario, ebn0_db, seed
                            )
                            writer.writerow(
                                {
                                    "line_code": line_code,
                                    "modulation": modulation_name,
                                    "scenario": scenario,
                                    "ebn0_db": ebn0_db,
                                    "seed": seed,
                                    "n_bits": result.n_bits,
                                    "bit_errors": result.bit_errors,
                                    "ber": f"{result.ber:.12g}",
                                    "violations": result.violations,
                                    "spectral_efficiency": result.spectral_efficiency,
                                }
                            )

    commit, dirty = _git_metadata()
    info = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "ebn0_db_values": EBN0_VALUES,
        "seeds": SEEDS,
        "repetitions_per_point": len(SEEDS),
        "message_characters": len(text),
        "message_bits_per_run": len(text) * 8,
        "line_codes": list(line_codes.NAMES),
        "modulations": list(modulation.NAMES),
        "scenarios": list(channel.SCENARIOS),
        "burst": {
            "stationary_bad_fraction": channel.P_BAD,
            "mean_burst_symbols": channel.MEAN_BURST,
            "bad_ebn0_db": channel.BAD_EBN0_DB,
        },
        "git_commit": commit,
        "git_dirty": dirty,
        "implementation_sha256": _implementation_fingerprint(),
        "raw_rows": total * len(EBN0_VALUES) * len(SEEDS),
    }
    RUN_INFO.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {RAW_CSV} and {RUN_INFO}")


if __name__ == "__main__":
    main()
