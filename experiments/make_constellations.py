"""Generate optional received 16-QAM constellation diagrams."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from sim.link import run_link
from sim.modulation import constellation
from sim.source import load_source


def main() -> None:
    output = Path("results/plots")
    output.mkdir(parents=True, exist_ok=True)
    text = load_source()
    ideal = constellation("16qam")
    fig, axes = plt.subplots(2, 3, figsize=(12, 8), sharex=True, sharey=True)
    for row, scenario in enumerate(("awgn", "burst")):
        for column, ebn0_db in enumerate((0, 10, 20)):
            result = run_link(text, "nrz", "16qam", scenario, ebn0_db, seed=0)
            rng = np.random.default_rng(12345)
            count = min(2500, result.rx_symbols.size)
            sample = rng.choice(result.rx_symbols, size=count, replace=False)
            axis = axes[row, column]
            axis.scatter(sample.real, sample.imag, s=4, alpha=0.18, color="#2563eb")
            axis.scatter(
                ideal.real,
                ideal.imag,
                s=45,
                marker="x",
                linewidths=1.8,
                color="#dc2626",
                label="ideal",
            )
            axis.set_title(f"{'AWGN' if scenario == 'awgn' else 'Rajadas'} — {ebn0_db} dB")
            axis.grid(True, alpha=0.25)
            axis.set_aspect("equal")
    for axis in axes[-1, :]:
        axis.set_xlabel("Componente em fase")
    for axis in axes[:, 0]:
        axis.set_ylabel("Componente em quadratura")
    fig.suptitle("Constelação 16-QAM recebida — NRZ")
    fig.tight_layout()
    fig.savefig(output / "constelacoes_16qam.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {output / 'constelacoes_16qam.png'}")


if __name__ == "__main__":
    main()
