"""Consistency demonstration for the presentation and video."""

import math

from sim import channel, line_codes, modulation
from sim.link import run_link
from sim.source import load_source


def main() -> None:
    text = load_source()
    print("TESTE IDEAL (Eb/N0 = infinito)")
    for line_code in line_codes.NAMES:
        for modulation_name in modulation.NAMES:
            result = run_link(text, line_code, modulation_name, "awgn", math.inf, seed=0)
            status = "OK" if result.recovered_text == text and not result.bit_errors else "FALHA"
            print(f"{line_code:17s} {modulation_name:5s}: {status}, BER={result.ber:.3g}")

    print("\nDEMONSTRAÇÃO A 20 dB")
    for scenario in channel.SCENARIOS:
        for line_code in line_codes.NAMES:
            for modulation_name in modulation.NAMES:
                result = run_link(text, line_code, modulation_name, scenario, 20.0, seed=0)
                first_errors = ",".join(map(str, result.error_indices[:8])) or "nenhum"
                print(
                    f"{scenario:5s} {line_code:17s} {modulation_name:5s}: "
                    f"erros={result.bit_errors:4d}, BER={result.ber:.3g}, "
                    f"bits incorretos=[{first_errors}]"
                )
    print("\nTrecho original:\n", text[:160].replace("\n", " "))
    burst = run_link(text, "nrz", "16qam", "burst", 20.0, seed=0)
    print("\nTrecho recebido (16-QAM/rajadas/20 dB):\n", burst.recovered_text[:160].replace("\n", " "))


if __name__ == "__main__":
    main()
