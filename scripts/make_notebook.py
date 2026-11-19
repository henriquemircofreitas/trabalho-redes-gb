"""Gera e executa o notebook de demonstração do vídeo (notebooks/demo_video.ipynb).

O notebook não reimplementa nada: apenas importa `sim` e os scripts de `experiments/`
e exibe os resultados versionados em `results/`.

Uso:
    uv run --group notebook python scripts/make_notebook.py
    uv run --group notebook python scripts/make_notebook.py --no-execute
"""

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "notebooks" / "demo_video.ipynb"

CELLS: list[tuple[str, str]] = []


def md(text: str) -> None:
    CELLS.append(("md", text.strip("\n")))


def code(text: str) -> None:
    CELLS.append(("code", text.strip("\n")))


md("""
# Simulador de transmissão digital — demonstração

`ASCII → bits → código de linha → modulação → canal → demodulação → decodificação → BER`

Este notebook **só importa** o código do repositório (`src/sim/` e `experiments/`) e os resultados
em `results/`. Nenhuma lógica foi reescrita aqui.

**Código de linha não é correção de erros:** ele define como os bits viram sinal (transições,
sincronismo, componente DC). Este trabalho mede os erros que sobram depois da decodificação.
""")

code("""
import json
import os
import sys
import time
from pathlib import Path

# Os scripts assumem a raiz do repositório como diretório de trabalho.
ROOT = Path.cwd()
if not (ROOT / "src" / "sim").exists():
    ROOT = ROOT.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "experiments"))

import numpy as np
from IPython.display import Image, Markdown, display

import demo
import make_plots
from sim import channel, line_codes, modulation, source
from sim.link import run_link

text = source.load_source()
print(f"Mensagem: {len(text):,} caracteres ASCII -> {len(source.text_to_bits(text)):,} bits")
""")

md("""
## 1. A cadeia de transmissão, etapa por etapa

Uma palavra curta passando por cada módulo de `src/sim/`: Manchester + QPSK em AWGN a 4 dB.
""")

code("""
msg = "Capitu"
code_name, mod_name, ebn0_db = "manchester", "qpsk", 4.0

bits = source.text_to_bits(msg)
chips = line_codes.encode(bits, code_name)
symbols = modulation.modulate(chips, mod_name)
eta = modulation.chips_per_symbol(mod_name) / line_codes.chips_per_bit(code_name)

rx_symbols = channel.transmit(symbols, ebn0_db, eta, "awgn", np.random.default_rng(5))
rx_chips = modulation.demodulate(rx_symbols, mod_name)
rx_bits, violations = line_codes.decode(rx_chips, code_name)

group = lambda b: " ".join("".join(map(str, b[i : i + 8])) for i in range(0, len(b), 8))
print(f"texto         : {msg!r}")
print(f"bits (8/char) : {group(bits)}")
print(f"chips         : {len(chips)} chips (Manchester: 2 por bit)")
print(f"símbolos QPSK : {len(symbols)} símbolos complexos, ex.: {np.round(symbols[:2], 3)}")
print(f"recebidos     : {np.round(rx_symbols[:2], 3)}  <- ruído a {ebn0_db:g} dB")
print(f"bits recebidos: {group(rx_bits)}")
print(f"erros de bit  : {int((bits != rx_bits).sum())}  | violações Manchester detectadas: {violations}")
print(f"texto recebido: {source.bits_to_text(rx_bits)!r}")
""")

md("""
## 2. Implementação funcionando: `experiments/demo.py`

Primeiro o **teste ideal** (Eb/N0 infinito): as nove combinações de código de linha × modulação
devem recuperar o texto exatamente. Depois, a 20 dB, os dois canais e os **índices dos bits
incorretos**.
""")

code("""
demo.main()
""")

md("""
Efeito prático das rajadas a 20 dB (NRZ + 16-QAM): quantos caracteres do livro chegam alterados.
""")

code("""
for scenario in channel.SCENARIOS:
    result = run_link(text, "nrz", "16qam", scenario, 20.0, seed=0)
    changed = [i for i, (a, b) in enumerate(zip(text, result.recovered_text, strict=True)) if a != b]
    print(f"{scenario:5s}: {result.bit_errors:4d} bits errados -> {len(changed):4d} de {len(text):,} caracteres alterados")

first = changed[0]
window = slice(max(first - 30, 0), first + 50)
flat = lambda s: s.replace("\\n", " ")
print(f"\\nprimeiro erro no caractere {first} (rajadas):")
print("  original:", flat(text[window]))
print("  recebido:", flat(result.recovered_text[window]))
""")

md("""
## 3. Metodologia e reprodução dos 990 ensaios

Configuração registrada em `results/run_info.json` e, em seguida, **toda a varredura executada de
novo** com `run_link`, comparada linha a linha com `results/raw.csv`.
""")

code("""
info = json.loads(Path("results/run_info.json").read_text(encoding="utf-8"))
print(f"bits por transmissão : {info['message_bits_per_run']:,}")
print(f"Eb/N0 (dB)           : {info['ebn0_db_values']}")
print(f"sementes             : {info['seeds']}")
print(f"códigos / modulações : {info['line_codes']} / {info['modulations']}")
print(f"canais               : {info['scenarios']}")
print(f"rajadas              : {info['burst']}")
print(f"ensaios registrados  : {info['raw_rows']}")
""")

code("""
rows = make_plots.read_rows()
saved = {
    (r["scenario"], r["line_code"], r["modulation"], int(r["ebn0_db"]), int(r["seed"])): (
        int(r["bit_errors"]),
        int(r["violations"]),
    )
    for r in rows
}

started = time.perf_counter()
trials = matches = 0
for scenario in info["scenarios"]:
    for line_code in info["line_codes"]:
        for modulation_name in info["modulations"]:
            for ebn0 in info["ebn0_db_values"]:
                for seed in info["seeds"]:
                    r = run_link(text, line_code, modulation_name, scenario, ebn0, seed)
                    trials += 1
                    matches += saved[(scenario, line_code, modulation_name, ebn0, seed)] == (
                        r.bit_errors,
                        r.violations,
                    )
            print(f"{scenario:5s} {line_code:17s} {modulation_name:5s}: {trials:3d} ensaios", flush=True)

print(f"\\n{matches}/{trials} ensaios idênticos aos de results/raw.csv ({time.perf_counter() - started:.0f} s)")
assert trials == len(rows) == matches
""")

md("""
## 4. Resultados

Médias de cinco sementes com IC de 95% (Student). Os números abaixo vêm de
`make_plots.aggregate`, a mesma função que gera as figuras.
""")

code("""
stats, eta_by_pair = make_plots.aggregate(rows)

def ber(line_code, mod, scenario, snr):
    mean, half, _ = stats[(line_code, mod, scenario, snr)]
    return f"{mean:.2e} ± {half:.1e}"

print("AWGN, Eb/N0 = 10 dB")
print(f"  NRZ + BPSK   : BER {ber('nrz', 'bpsk', 'awgn', 10)}")
print(f"  NRZ + 16-QAM : BER {ber('nrz', '16qam', 'awgn', 10)}")
print("Rajadas, Eb/N0 = 20 dB (o ruído extra não some com mais potência)")
print(f"  NRZ + BPSK               : BER {ber('nrz', 'bpsk', 'burst', 20)}")
print(f"  Manchester dif. + 16-QAM : BER {ber('diff_manchester', '16qam', 'burst', 20)}")
zero_at_20 = all(v[0] == 0 for k, v in stats.items() if k[2] == "awgn" and k[3] == 20)
print("AWGN, Eb/N0 = 20 dB:", "BER média zero nas 9 combinações" if zero_at_20 else "há erros")
""")

code("""
display(Image(filename="results/plots/ber_nrz.png", width=1100))
""")

code("""
display(Image(filename="results/plots/comparacao_canais_nrz.png", width=1100))
""")

code("""
display(Image(filename="results/plots/constelacoes_16qam.png", width=850))
""")

md("""
## 5. Compromisso entre BER e eficiência espectral

Eb/N0 necessário para BER = 10⁻³ em AWGN, interpolado por `make_plots.required_ebn0`.
""")

code("""
labels = make_plots.LABELS
print(f"{'código':24s} {'modulação':10s} {'η (bit/s/Hz)':>13s} {'Eb/N0 p/ BER=1e-3':>18s}")
for line_code in line_codes.NAMES:
    for mod in modulation.NAMES:
        need = make_plots.required_ebn0(stats, line_code, mod, "awgn")
        need_text = f"{need:.2f} dB" if need is not None else "não atingido"
        print(f"{labels[line_code]:24s} {labels[mod]:10s} {eta_by_pair[(line_code, mod)]:13.1f} {need_text:>18s}")
""")

code("""
display(Markdown(Path("results/tradeoff.md").read_text(encoding="utf-8")))
""")

md("""
## Conclusão

- **AWGN** se combate com potência: a BER cai quando Eb/N0 sobe; BPSK e QPSK seguem a curva teórica.
- **Rajadas** criam um piso de BER que mais potência não remove.
- **16-QAM** entrega 4 bit/s/Hz com NRZ, mas exige mais Eb/N0 (≈ 10,4 dB contra ≈ 6,7 dB do BPSK para BER = 10⁻³).
- **Manchester** custa metade da eficiência espectral e cerca de 3 dB neste receptor; em troca dá sincronismo e detecção de violações.
- A escolha depende de potência disponível, largura de banda e natureza do canal.

Código, testes, dados brutos e este notebook estão no repositório do GitHub.
""")


def build() -> nbformat.NotebookNode:
    notebook = new_notebook()
    notebook.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    cells = []
    for index, (kind, source_text) in enumerate(CELLS):
        factory = new_markdown_cell if kind == "md" else new_code_cell
        cell = factory(source_text)
        cell["id"] = f"cell-{index:02d}"  # stable ids keep regenerated diffs small
        cells.append(cell)
    notebook.cells = cells
    return notebook


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-execute", action="store_true", help="grava o notebook sem saídas")
    args = parser.parse_args()

    notebook = build()
    if not args.no_execute:
        NotebookClient(
            notebook,
            timeout=600,
            kernel_name="python3",
            record_timing=False,
            resources={"metadata": {"path": str(ROOT)}},
        ).execute()
    OUT.parent.mkdir(exist_ok=True)
    nbformat.write(notebook, OUT)
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
