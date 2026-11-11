"""Create BER figures and the BER/spectral-efficiency trade-off table."""

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAW = Path("results/raw.csv")
PLOTS = Path("results/plots")
T_VALUE_95_DF4 = 2.776
TARGET_BER = 1e-3
FIXED_EBN0 = 10
LABELS = {
    "nrz": "NRZ",
    "manchester": "Manchester",
    "diff_manchester": "Manchester diferencial",
    "bpsk": "BPSK",
    "qpsk": "QPSK",
    "16qam": "16-QAM",
    "awgn": "AWGN",
    "burst": "Rajadas",
}
COLORS = {"bpsk": "#2563eb", "qpsk": "#16a34a", "16qam": "#dc2626"}


def read_rows() -> list[dict[str, str]]:
    with RAW.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def aggregate(rows: list[dict[str, str]]):
    grouped: dict[tuple[str, str, str, int], list[float]] = defaultdict(list)
    n_bits: dict[tuple[str, str, str, int], int] = {}
    eta: dict[tuple[str, str], float] = {}
    for row in rows:
        key = (row["line_code"], row["modulation"], row["scenario"], int(row["ebn0_db"]))
        grouped[key].append(float(row["ber"]))
        n_bits[key] = int(row["n_bits"])
        eta[(row["line_code"], row["modulation"])] = float(row["spectral_efficiency"])

    stats = {}
    for key, values in grouped.items():
        sample = np.asarray(values, dtype=float)
        mean = float(sample.mean())
        half = float(T_VALUE_95_DF4 * sample.std(ddof=1) / math.sqrt(sample.size))
        # Zero observed errors are displayed as a 95% upper bound (rule of three).
        display = mean if mean > 0 else 3.0 / (n_bits[key] * sample.size)
        stats[key] = (mean, half, display)
    return stats, eta


def theoretical_ber(mod: str, ebn0_db: np.ndarray) -> np.ndarray:
    gamma = 10.0 ** (ebn0_db / 10.0)
    erfc = np.vectorize(math.erfc)
    if mod in {"bpsk", "qpsk"}:
        return 0.5 * erfc(np.sqrt(gamma))
    return 0.375 * erfc(np.sqrt(0.4 * gamma))


def plot_ber(stats) -> None:
    snrs = list(range(0, 21, 2))
    for line_code in ("nrz", "manchester", "diff_manchester"):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
        for axis, scenario in zip(axes, ("awgn", "burst"), strict=True):
            for mod in ("bpsk", "qpsk", "16qam"):
                values = [stats[(line_code, mod, scenario, snr)] for snr in snrs]
                means = np.array([value[0] for value in values])
                display = np.array([value[2] for value in values])
                half = np.array([value[1] for value in values])
                lower = np.minimum(half, display * 0.8)
                axis.errorbar(
                    snrs,
                    display,
                    yerr=np.vstack((lower, half)),
                    marker="o",
                    capsize=3,
                    linewidth=1.5,
                    color=COLORS[mod],
                    label=LABELS[mod],
                )
                zero_points = means == 0
                if np.any(zero_points):
                    axis.scatter(
                        np.asarray(snrs)[zero_points],
                        display[zero_points],
                        marker="v",
                        facecolors="none",
                        edgecolors=COLORS[mod],
                        zorder=5,
                    )
                if line_code == "nrz" and scenario == "awgn":
                    dense = np.linspace(0, 20, 250)
                    axis.plot(
                        dense,
                        theoretical_ber(mod, dense),
                        "--",
                        color=COLORS[mod],
                        alpha=0.55,
                        label=f"{LABELS[mod]} teórica",
                    )
            axis.set_yscale("log")
            axis.set_ylim(1e-7, 1)
            axis.set_xlabel("Eb/N0 por bit da mensagem (dB)")
            axis.set_title(LABELS[scenario])
            axis.grid(True, which="both", alpha=0.25)
        axes[0].set_ylabel("BER média (IC 95%, n=5)")
        handles, labels = axes[0].get_legend_handles_labels()
        if line_code != "nrz":
            handles, labels = axes[1].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.03))
        fig.suptitle(f"BER × Eb/N0 — {LABELS[line_code]}")
        fig.tight_layout(rect=(0, 0.08, 1, 0.95))
        fig.savefig(PLOTS / f"ber_{line_code}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


def plot_channel_comparison(stats) -> None:
    snrs = list(range(0, 21, 2))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for axis, mod in zip(axes, ("bpsk", "qpsk", "16qam"), strict=True):
        for scenario, style in (("awgn", "-"), ("burst", "--")):
            display = [stats[("nrz", mod, scenario, snr)][2] for snr in snrs]
            axis.plot(snrs, display, style, marker="o", label=LABELS[scenario])
        axis.set_yscale("log")
        axis.set_ylim(1e-7, 1)
        axis.set_title(LABELS[mod])
        axis.set_xlabel("Eb/N0 (dB)")
        axis.grid(True, which="both", alpha=0.25)
        axis.legend()
    axes[0].set_ylabel("BER média — NRZ")
    fig.suptitle("Comparação direta dos cenários de canal")
    fig.tight_layout()
    fig.savefig(PLOTS / "comparacao_canais_nrz.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def required_ebn0(stats, line_code: str, mod: str, scenario: str) -> float | None:
    points = [(snr, stats[(line_code, mod, scenario, snr)][0]) for snr in range(0, 21, 2)]
    if points[0][1] <= TARGET_BER:
        return float(points[0][0])
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if y0 > TARGET_BER and 0 < y1 <= TARGET_BER:
            fraction = (math.log10(TARGET_BER) - math.log10(y0)) / (
                math.log10(y1) - math.log10(y0)
            )
            return x0 + fraction * (x1 - x0)
    return None


def verdict(line_code: str, mod: str) -> str:
    modulation_text = {
        "bpsk": "canal com pouca SNR; prioriza robustez",
        "qpsk": "equilíbrio entre robustez e largura de banda",
        "16qam": "SNR alta e largura de banda escassa",
    }[mod]
    coding_text = {
        "nrz": "máxima eficiência",
        "manchester": "sincronismo e detecção de violações",
        "diff_manchester": "sincronismo e tolerância a inversão de polaridade após referência",
    }[line_code]
    return f"{modulation_text}; {coding_text}"


def write_tradeoff(stats, eta) -> None:
    output_rows = []
    for line_code in ("nrz", "manchester", "diff_manchester"):
        for mod in ("bpsk", "qpsk", "16qam"):
            awgn_req = required_ebn0(stats, line_code, mod, "awgn")
            burst_req = required_ebn0(stats, line_code, mod, "burst")
            output_rows.append(
                {
                    "line_code": line_code,
                    "modulation": mod,
                    "spectral_efficiency_bits_s_hz": eta[(line_code, mod)],
                    "required_ebn0_awgn_db_for_ber_1e-3": awgn_req,
                    "required_ebn0_burst_db_for_ber_1e-3": burst_req,
                    "ber_awgn_at_10_db": stats[(line_code, mod, "awgn", FIXED_EBN0)][0],
                    "ber_burst_at_10_db": stats[(line_code, mod, "burst", FIXED_EBN0)][0],
                    "best_when": verdict(line_code, mod),
                }
            )

    csv_path = Path("results/tradeoff.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    def req(value):
        return "não atingido" if value is None else f"{value:.2f} dB"

    lines = [
        "# Compromisso entre BER e eficiência espectral",
        "",
        "Valores de Eb/N0 foram interpolados em escala logarítmica da BER média.",
        "",
        "| Código | Modulação | η (bit/s/Hz) | Eb/N0 p/ BER=10⁻³ AWGN | Eb/N0 p/ BER=10⁻³ rajadas | BER AWGN @10 dB | BER rajadas @10 dB | Indicação |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in output_rows:
        lines.append(
            f"| {LABELS[row['line_code']]} | {LABELS[row['modulation']]} | "
            f"{row['spectral_efficiency_bits_s_hz']:.1f} | "
            f"{req(row['required_ebn0_awgn_db_for_ber_1e-3'])} | "
            f"{req(row['required_ebn0_burst_db_for_ber_1e-3'])} | "
            f"{row['ber_awgn_at_10_db']:.3g} | {row['ber_burst_at_10_db']:.3g} | "
            f"{row['best_when']} |"
        )
    Path("results/tradeoff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows = read_rows()
    expected = 3 * 3 * 2 * 11 * 5
    if len(rows) != expected:
        raise ValueError(f"raw.csv has {len(rows)} rows; expected {expected}")
    stats, eta = aggregate(rows)
    plot_ber(stats)
    plot_channel_comparison(stats)
    write_tradeoff(stats, eta)
    print(f"Wrote figures to {PLOTS} and trade-off tables to results/")


if __name__ == "__main__":
    main()
