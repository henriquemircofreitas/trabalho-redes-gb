# Decision log

Every design decision we make, with the reason, so we can explain "why we chose to implement it this way" in the presentation. Newest at the bottom.

Format: **Decision** — what we chose. **Why** — the reason. **Rejected** — what else we considered and why not.

---

## D1 — Line coding sits inside a single chain, before modulation

**Decision:** One end-to-end pipeline: message bits → line code → chips → modulation → channel → demodulation → line decoding → bits. Line codes are restricted to ones that produce *binary* chips: **NRZ** (baseline, no line code), **Manchester**, **Differential Manchester (biphase)**.

**Why:**
- It is literally the pipeline the assignment describes (geração → codificação de linha → modulação → canal → demodulação → decodificação → métricas).
- Binary chips can feed any modulation, so every line code × modulation combination works (3 × 3 grid of results).
- It gives us concrete material for the required "line coding vs. error-correction coding" explanation:
  - Manchester doubles the chips (halves spectral efficiency) but invalid chip pairs (`00`/`11`) reveal errors — *detection*, not correction.
  - Differential Manchester propagates errors (1 chip error → 2 bit errors) but is immune to a 180° phase inversion.

**Rejected:**
- *Two separate branches* (line coding over its own baseband channel, modulation on another) — cleaner, but the parts never interact and it reads less like one end-to-end system.
- *AMI in the chain* — AMI is ternary (−1, 0, +1) and does not map naturally onto QPSK/16-QAM symbols. AMI is only an example in the assignment, so dropping it is allowed.

## D2 — The x-axis is Eb/N0 per message bit

**Decision:** Every BER curve uses **Eb/N0 (dB), where Eb is the energy per message bit** (the original ASCII bit, before line coding). The noise for each run is derived from it: energy per chip = Eb × (message bits / chips), energy per symbol = energy per chip × chips per symbol.

**Why:**
- The assignment demands "parâmetros equivalentes nas comparações". Giving every line code × modulation combination the same energy per *message* bit is the only fair basis: the cost of each scheme shows up in the curve instead of being hidden.
- Manchester sends 2 chips per bit, so each chip gets half the energy — its redundancy cost becomes visible, which is exactly what we want to discuss.
- It is the standard axis for theoretical BER curves, so we can overlay theory (optional deepening item).
- In the presentation we show the one-line conversion to per-symbol SNR (Es/N0 = Eb/N0 × bits per symbol) so the assignment's word "SNR" is explicitly covered.

**Rejected:**
- *Es/N0 per symbol* — penalises 16-QAM (4 chips per symbol) and hides the per-bit cost.
- *SNR per chip* — hides Manchester's cost entirely (each chip would get full energy).

## D3 — Hard-decision demodulation; the line decoder only sees chips

**Decision:** The demodulator decides each symbol and outputs **chips (0/1)**. The line decoder works purely on chips. For Manchester: `01`→0, `10`→1; `00`/`11` is a **violation** (detected error), resolved by a fixed rule — take the first chip. Violations are counted as an extra metric.

**Why:**
- One uniform interface (chips in, chips out) lets every modulation plug into every line code with no special cases.
- It produces a concrete, explainable result: with hard decisions and Eb/N0 per message bit (D2), Manchester should come out ~3 dB worse than NRZ, since each chip gets half the energy and is decided alone. Presentation line: "this is the price of hard decisions; a soft-decision receiver would recover it."
- Counting violations shows Manchester's *detection* ability (errors detected vs. errors that actually happened) — feeds the line coding vs. error-correction discussion.

**Rejected:**
- *Soft decision* (pass real values; Manchester decodes as r1 − r2, recovering full bit energy) — simple for BPSK, but awkward for QPSK/16-QAM where a bit's two chips may land in different symbols with different reliability. More code and a blurrier module boundary for a gain we can explain verbally instead.

## D4 — Python + NumPy + Matplotlib, plain scripts, managed with uv

**Decision:** Python, vectorised with NumPy, plots with Matplotlib. Experiments are plain scripts — one command per experiment writes raw results (CSV) and plots (PNG). Dependencies pinned and managed with `uv` (`uv sync`, then `uv run ...`).

**Why:**
- Experiment size is ~18 combinations × 8+ Eb/N0 points × 5 seeds × 100k+ bits ≈ 72M+ bits; vectorised NumPy runs this in seconds to minutes.
- Plain scripts make "reproduce every plot with one command" trivial — the rubric grades reproducibility.
- `uv` gives a two-command install in the README and pinned versions for reproducible results.

**Rejected:**
- *Jupyter as the source of truth* — hidden state and cell order make reproduction fragile; notebooks diff badly with two people editing. (A notebook may still be added later for the video/constellation demo, reading the CSVs.)
- *MATLAB/Octave* — license cost / slower and clunkier setup.
- *C++/Rust/JS* — faster, but we'd write numerics and plotting plumbing ourselves with no grading benefit.

## D5 — Second channel scenario: burst noise (Gilbert–Elliott)

**Decision:** Besides plain AWGN, a **burst channel** modelled as a two-state Gilbert–Elliott process: a *good state* (background AWGN only) and a *bad state* (background AWGN + much stronger extra noise), with a fixed mean burst length. The x-axis stays the background Eb/N0 (D2); the burst adds noise on top. Burst parameters (fraction of time in the bad state, mean burst length, bad-state noise level) are fixed and logged with the results. *(Amended by D14: the bad-state noise is a fixed absolute level, not a multiplier of the background noise.)*

**Why:**
- It is the assignment's own first example ("ruído em rajadas").
- It needs no new receiver machinery — hard-decision demodulation (D3) works unchanged.
- It gives the richest contrast with AWGN:
  - errors cluster → recovered text shows visible runs of garbage (good for the video);
  - a burst hits both chips of a Manchester pair → violations behave differently than in AWGN;
  - Differential Manchester's error propagation compounds inside a burst;
  - BER floors at high Eb/N0 — more power does not fix bursts.

**Rejected:**
- *Rayleigh flat fading* — realistic, but random phase breaks QPSK/16-QAM without channel estimation/equalisation; either an unjustified "perfect CSI" shortcut or a lot more code.
- *Impulsive noise* — simpler but less interesting: isolated spikes, no clustering, looks like "AWGN with outliers".

## D6 — One long ASCII text is the only source

**Decision:** Every transmission — BER sweeps included — sends the same long public-domain ASCII text (≥ 12,500 characters ⇒ ≥ 100,000 message bits; e.g. a Machado de Assis excerpt). The 5 repetitions vary only the noise seed. No random-bit source exists.

**Why:**
- The rubric stresses end-to-end implementation (item 2) and message recovery. "Every point on our plots comes from transmitting real text" is a strong presentation line, and any run can be shown as recovered text.
- One source means one pipeline — no separate "statistics mode" vs "demo mode".

**Known effect (discussion point, not a flaw):** ASCII is not random — the top bit of every byte is 0. With 16-QAM this skews which constellation points get used, so measured BER may drift slightly from theory. Manchester cancels the skew (every bit becomes `01` or `10`).

**Rejected:**
- *Random bits for sweeps, ASCII only for demos* — statistically cleaner, but the graded sweeps would not be the ASCII → … → message system.
- *Short message repeated to 100k bits* — still skewed, and repetitive.

## D7 — One shared Eb/N0 grid: 0 to 20 dB, step 2 dB (11 points)

**Decision:** All 18 combinations (3 line codes × 3 modulations × 2 channel scenarios) use the same grid: Eb/N0 = 0, 2, 4, …, 20 dB. Points where zero errors are observed are not plotted as 0 (impossible on a log axis) but as an upper bound (rule of three: BER < 3/N at 95% confidence, N = message bits sent).

**Why:**
- More than the required 8 points, and wide enough for the slowest combination: 16-QAM needs ~12 dB for BER ≈ 10⁻⁵, plus ~3 dB for Manchester with hard decisions (D3) ⇒ ~15 dB.
- Every combination reaches its error-free region, which the high-SNR consistency test needs.
- A shared grid keeps comparisons direct ("parâmetros equivalentes") and lets the BER × spectral efficiency table read values at the same Eb/N0.
- Cost: 11 × 18 × 5 ≈ 1,000 runs of 100k bits — minutes in NumPy (D4).

**Rejected:**
- *0–14 dB (exactly 8 points)* — cuts off the Manchester + 16-QAM curve before it drops.
- *Per-modulation grids* — prettier curves, but no shared x-values for comparisons and the trade-off table.

## D8 — Variability: mean BER with 95% confidence intervals (Student's t, n = 5)

**Decision:** Each point on a BER × Eb/N0 curve is the mean of the 5 per-seed BERs, with error bars = 95% confidence interval: mean ± t · s/√5, t ≈ 2.776 (4 degrees of freedom). The lower end is clipped where it would go ≤ 0 on the log axis — stated on the slide. The raw CSV keeps every per-seed BER so anyone can recompute.

**Why:**
- Rubric item 7 grades "análise de variabilidade"; a confidence interval is a statistic we can *reason* with: "curves are distinguishable where their intervals do not overlap".
- Explaining why intervals widen at low BER (few errors ⇒ large relative uncertainty) shows statistical understanding — what the grader rewards ("capacidade de interpretar os resultados").

**Rejected:**
- *Min–max bars* — honest but descriptive only; less to analyse.
- *Mean ± 1 standard deviation* — neither a confidence interval nor the true range; easy to misread.

## D9 — Gray mapping, constellations normalised to unit average energy

**Decision:** QPSK and 16-QAM use **Gray-coded** constellations (adjacent points differ in exactly one chip). Every constellation (BPSK included) is scaled to average symbol energy 1.

**Why:**
- With hard decisions (D3) most symbol errors land on a neighbouring point; Gray mapping makes such an error cost ~1 chip instead of up to 4. Presentation line: "Gray mapping makes a symbol error cost about one bit."
- Textbook theoretical BER curves assume Gray mapping, so the optional theory overlay lines up.
- Unit average energy keeps the noise derivation from D2 identical for all modulations (just multiply by chips per symbol).
- Cost: ~10 lines of lookup tables.

**Rejected:**
- *Natural binary labelling* — neighbours can differ in 2+ chips, inflating BER for reasons unrelated to the modulation itself — a confounder we would have to explain away.

## D10 — Nominal spectral efficiency = message bits per chip × chips per symbol (ideal Nyquist)

**Decision:** η (bits/s/Hz) = (message bits per chip) × (chips per symbol), assuming ideal Nyquist pulses (bandwidth = symbol rate).

| | BPSK | QPSK | 16-QAM |
|---|---|---|---|
| NRZ | 1 | 2 | 4 |
| Manchester / Diff. Manchester | 0.5 | 1 | 2 |

**Why:**
- The assignment asks for *nominal* efficiency — a calculated value, not a measurement.
- Simple, exact, and it makes the line-code cost visible: Manchester halves η. Together with its ~3 dB loss (D3), Manchester pays in both bandwidth and power, buying violation detection and clock transitions — the key insight of the trade-off table.
- Slide note: real systems use roll-off α, dividing every entry by (1 + α) without changing the ranking.

**Rejected:**
- *Raised-cosine roll-off in the formula* — more realistic, but an extra parameter that scales every entry equally and changes no comparison.
- *Measured η from an FFT of the signal* — not "nominal", needs pulse shaping and oversampling we don't simulate, much more code.

## D11 — Trade-off table: one row per line code × modulation, power cost at BER = 10⁻³

**Decision:** 9 rows (3 line codes × 3 modulations). Columns:

| Column | Meaning |
|---|---|
| η (bits/s/Hz) | from D10 |
| Required Eb/N0 for BER = 10⁻³ — AWGN | read off the curve, interpolated between grid points — the power cost |
| Required Eb/N0 for BER = 10⁻³ — burst | same under bursts; "not reached" if the curve floors (itself a finding) |
| BER at a fixed Eb/N0 (e.g. 10 dB), both channels | direct snapshot |
| Best when… | one-line verdict, e.g. "16-QAM/NRZ: plenty of SNR, scarce bandwidth" |

**Why:**
- The assignment asks for a "tabela de compromisso" and *when* each modulation is most suitable; required Eb/N0 vs η is exactly the power-vs-bandwidth trade-off.
- Target 10⁻³ because with 100k bits it means ~100 errors per seed — statistically solid, tight intervals (D8). At 10⁻⁵ it would be ~1 error — noise.

**Rejected:**
- *Target 10⁻⁴* — closer to real links, but ~10 errors per seed; would need more bits (and justification) for solid numbers.
- *Only η and BER at one Eb/N0* — loses the required-power column, the heart of the trade-off.

## D12 — Consistency test in two layers: noiseless pytest + 20 dB demo

**Decision:**
1. **Automated test (pytest), noiseless channel:** all 9 line code × modulation combinations must recover the source text *exactly* (zero bit errors, identical string).
2. **Demo at 20 dB** (top of the grid), all 18 combinations: print BER and a snippet of the recovered text. Expected: AWGN ⇒ perfect text; burst ⇒ residual errors even at 20 dB (the floor from D5) — the divergence we explain.

Protocol assumption: Differential Manchester encoder and decoder share a fixed starting reference level (**low**).

Fact checked: no padding is ever needed — 8 bits per character always divides into 1, 2 or 4 chips per symbol.

**Why:**
- The noiseless test is the rubric's "validação funcional" (item 2), runs in seconds, and guards against regressions while two people write code.
- The 20 dB demo covers the "explicar eventuais divergências" part with a real, explainable divergence (burst floor) — good video material.

**Rejected:**
- *Only the 20 dB demo* — no automated guarantee; a lucky noise draw can hide a bug.
- *Only the noiseless test* — proves plumbing, misses the "explain divergences" requirement.

## D13 — Optional deepening: both, kept narrow

**Decision:**
- **Theory overlay:** dashed theoretical BER curves on the AWGN plot for the NRZ rows — BPSK/QPSK: Q(√(2·Eb/N0)); 16-QAM: standard Gray approximation. Manchester variants get the same curves shifted by +3 dB, visually checking the D3 prediction.
- **Constellation scatter plots:** 16-QAM, received symbols at ~3 Eb/N0 values (low, mid, high), for both channel scenarios.

**Why:**
- If simulated curves sit on the theory lines, the simulator is validated by an *independent* argument — stronger than any unit test. Feeds rubric items 7–8 ("análise", "conclusões técnicas").
- The scatter plots are the most visual material for the 5-minute video: under bursts, a tight cloud plus scattered outliers.
- Cost: roughly an hour in total (~10 lines of theory formulas, ~20 lines of plotting).

**Rejected:**
- *Theory only* — keeps the strongest evidence but loses the visual.
- *Neither* — saves an hour, loses the cheapest validation and the best video visual.

## D14 — Bad-state noise is a fixed absolute level (amends D5)

**Decision:** In the burst channel the bad state adds noise at a **fixed level, independent of the Eb/N0 sweep**: bad-state Eb/N0 = **0 dB** (same per-message-bit units as D2, so every combination suffers an equivalent burst). Starting values (tunable after a first run, then frozen and logged):
- fraction of time in the bad state: **1%**
- mean burst length: **20 symbols**
- the burst process advances per **symbol** (fixed symbol rate, matching the bandwidth assumption in D10)

**Why:**
- A noise *multiplier* (the original D5 wording) shrinks with the background noise as Eb/N0 rises — bursts would vanish at high SNR and there would be no floor. A fixed level produces a real floor: BER_floor ≈ (fraction in bad state) × BER(0 dB). Predictable on paper ⇒ another independent check against the plot.
- Predicted floors ≈ 8·10⁻⁴ (NRZ-BPSK) to 1–2·10⁻³ (16-QAM): some combinations reach the 10⁻³ target of D11 under bursts and some don't — a discriminating table.
- Per-symbol bursts: a 20-symbol burst corrupts 4× more chips under 16-QAM than under BPSK — realistic, and one more effect to explain.

**Rejected:**
- *Bad-state noise as a multiplier of the background noise* — no floor; loses the "more power doesn't fix bursts" argument and the 20 dB residual-error demo (D12).

## D15 — One module per pipeline stage; a raw-results CSV is the run ↔ plot contract

**Decision:**
```
src/sim/
  source.py        text ⇄ message bits
  line_codes.py    NRZ, Manchester, Diff. Manchester: bits ⇄ chips (+ violation count)
  modulation.py    BPSK, QPSK, 16-QAM: chips ⇄ symbols (Gray, unit energy)
  channel.py       AWGN and burst: symbols + Eb/N0 + seed → noisy symbols
  link.py          one transmission end to end → BER, violations, recovered text
experiments/
  run_sweep.py     full grid → results/raw.csv (one row per combination × Eb/N0 × seed)
  make_plots.py    raw.csv → BER curves, trade-off table, constellations
  demo.py          20 dB consistency demo (D12)
tests/             noiseless pytest (D12) + small per-stage tests
```
Each stage is a pair of pure functions (encode/decode, modulate/demodulate) on NumPy arrays. Plots never re-run the simulation — they only read the CSV.

**Why:**
- Module boundaries are where the pair splits the work; the function signatures are what we agree on before coding.
- Each stage is testable in isolation.
- The CSV contract gives "resultados brutos e scripts para reproduzir todos os gráficos" — explicitly required — and lets plotting start on day one from a fake CSV.

**Rejected:**
- *Single simulator.py* — constant merge conflicts with two people, no natural split.
- *Class hierarchy (Modulator/Channel base classes)* — ceremony for 3 line codes and 3 modulations; plain functions plus a dictionary lookup do the same job.

## D16 — Work split along the D15 boundary: link vs. channel & experiments

**Decision:**

| | **Person 1 — Link** | **Person 2 — Channel & experiments** |
|---|---|---|
| Code | `source.py`, `line_codes.py`, `modulation.py`, `link.py`, noiseless pytest, `demo.py` | `channel.py` (AWGN + burst), `run_sweep.py`, `make_plots.py` (curves + CI, theory overlay, constellations, trade-off table) |
| Presents | pipeline, line coding vs. error-correction coding, Manchester violations, Gray mapping, consistency test | channel models, Eb/N0 fairness, BER curves & variability, trade-off table & conclusions |

Shared: video and README (each writes their own section).

**Roles:** Person 1 (Link) = the plan author (who made decisions D1–D16 — the link side depends most on that reasoning). Person 2 (Channel & experiments) = the colleague — that side is specified mostly by formulas and parameters (D2, D5, D7, D8, D10, D11, D13, D14) and is easiest to hand off cold.

**Why:**
- Both can start on day one: Person 2 builds the channel and plots against a fake CSV while Person 1 builds the chain; they meet at `link.py` and `raw.csv`.
- Roughly equal load: the chain has more modules, the experiments side carries the statistics and analysis.
- Each person presents what they built — rubric item 1 (balanced participation) and the README's "divisão de responsabilidades".

**Rejected:**
- *Split by modulation/line code* — both touch every module ⇒ conflicts, inconsistent style.
- *One codes, one analyses/presents* — unbalanced; the non-coder struggles with questions on the code.

## D17 — Source text is Portuguese, transliterated to 7-bit ASCII; unreadable bytes decode as `?`

**Decision:**
- `data/source.txt` is a Portuguese public-domain text (e.g. Machado de Assis), ≥ 12,500 characters, **transliterated once to 7-bit ASCII** (Python `unicodedata` NFKD → ASCII, dropping the combining accents: "ação" → "acao"). The one-off conversion snippet is kept so the file is reproducible.
- When decoding received bits, any byte that is not printable ASCII is shown as `?` — decoding never crashes, so garbled text still prints in the demo.

**Why:**
- The assignment literally says "mensagem em ASCII". UTF-8 accents would turn one character into 2 bytes, breaking "1 character = 8 bits" and the no-padding fact (D12).
- Portuguese keeps the garbled output readable for a Brazilian audience in the video.
- The `?` rule makes corrupted output visible instead of crashing.

**Rejected:**
- *English text* — natively ASCII and equally valid, just less natural for the audience.
- *UTF-8 with accents* — not ASCII; violates the requirement.

## D18 — Interface contract frozen in `docs/interface.md`

**Decision:** The module signatures and the `raw.csv` columns in `docs/interface.md` are the contract between the pair; changed only by agreement. Two details settled while drafting it:
- **Differential Manchester also reports violations** — it has a mid-bit transition on every bit, so `00`/`11` is invalid there too. Both line codes get the detection metric.
- **The channel only needs η (message bits per symbol)** to scale noise fairly (D2) — it never needs to know which line code or modulation produced the symbols.
- **Common random numbers:** seeds 0..4 via `np.random.default_rng(seed)`; every combination sees the same noise for the same seed, which reduces variance in the *comparisons* between combinations.

**Why:** A written contract lets both work in parallel from day one without blocking each other (D16).

## D19 — Timeline, repo and deliverable language

**Decision — milestones (today 8/11; deadline 19/11, Moodle link by 19h):**

| Date | Milestone | Who |
|---|---|---|
| 8–9/11 | Create GitHub repo, push this plan (`CONTEXT.md`, `docs/`), commit `data/source.txt`, scaffold `uv` + pytest | P1 |
| 9/11 | Colleague reads the plan; objections now, not later | P2 |
| 12/11 | **Integration:** noiseless pytest green for all 9 combinations (P1); `transmit()` + plots from a fake CSV (P2) | both |
| 14/11 | First full sweep → real `raw.csv`; check predictions (Manchester ≈ +3 dB, burst floor ≈ 10⁻³, curves on theory); tune and freeze burst values (D14) | P2 |
| 16/11 | Results frozen; draft slides and README | both |
| 17/11 | Record video (≤ 5 min), commit to repo | both |
| 18/11 | Buffer: rehearse the 10-min talk, final README pass | both |
| 19/11 | Moodle link before 19h; present | both |

**Decision — repo rules:**
- **Public** GitHub repo — the professor needs no invite.
- **Video committed to the repo** (MP4 < ~50 MB, or attached to a GitHub Release if larger). Rubric item 10 says "vídeo disponibilizado no GitHub"; a YouTube link alone is risky against that wording.
- **Language:** README, slides and video in **Portuguese** (course language); code and identifiers in English; planning docs (`docs/`, `CONTEXT.md`) may stay in English.

**Why:** An early integration point (12/11) surfaces interface mismatches with a week to spare; freezing results on 16/11 leaves three days for the part the grade weighs most — interpretation and presentation.

## D20 — Schemes are chosen by name; the scheme table is private to each module

**Decision:** `line_codes` and `modulation` expose functions that take the scheme name as a parameter — `encode(bits, "manchester")`, `decode(chips, "manchester")`, `chips_per_bit("manchester")`, `modulate(chips, "16qam")`, `demodulate(symbols, "16qam")`, `chips_per_symbol("16qam")` — plus a `NAMES` tuple to iterate over. The name → implementation table lives inside each module. Unknown name ⇒ `KeyError`. (Replaces the `LINE_CODES`/`CHIPS_PER_BIT` dictionaries drafted in D18; `docs/interface.md` updated.)

**Why:**
- D18's draft had two dictionaries describing the same schemes (`LINE_CODES` and `CHIPS_PER_BIT`) — add a scheme to one, forget the other, and they silently disagree. One private table cannot drift.
- Smallest surface for every caller: `link.py` reads like the pipeline (encode → modulate → transmit → demodulate → decode), the sweep just loops over `NAMES`, and the name strings are exactly the CSV values — no translation step.

**Rejected:**
- *A record per scheme* (`LineCode(name, chips_per_bit, encode, decode)`) — also drift-free, but every caller must learn the record's shape and unpack it.
- *Separate dictionaries as drafted in D18* — drift risk.

## D21 — One generic modulator over three constellation tables

**Decision:** `modulation.py` has a single implementation driven by a private table of constellations (`bpsk`: 2 points, `qpsk`: 4, `16qam`: 16). Index *i* in a table is the point whose chip label is *i* read as binary, with Gray order baked into the table and scaling to unit average energy applied when the table is built.
- modulate: chips → groups of `chips_per_symbol` → index → table[index]
- demodulate: nearest point (argmin |symbol − point| over the table) → index → chips

A public `constellation(mod)` returns the ideal points, so the constellation scatter plots (D13) mark them from the same table.

**Why:**
- The three modulations differ *only* in their table; one implementation (~25 lines) means one place for bugs. A new modulation (8-PSK, 64-QAM) would be just a new table.
- Gray mapping and unit energy (D9) are checked by one test looping over all tables (neighbours differ in 1 chip; mean |point|² = 1).
- Cost of brute-force nearest point: ≤ 100k × 16 distances — milliseconds in NumPy.

**Rejected:**
- *Three hand-written pairs* (sign of real part; signs of real/imag; per-axis thresholds for 16-QAM) — textbook and slightly faster, but three implementations each with their own Gray/energy logic and tests, for no measurable gain.

## D22 — Parameters are constants where they are used; every sweep writes a run snapshot

**Decision:**
- Burst constants stay in `channel.py` (D14); the Eb/N0 grid and seeds are constants at the top of `run_sweep.py`.
- `run_sweep.py` writes `results/raw.csv` **and** `results/run_info.json`: grid, seeds, burst constants (read from `channel.py`, never copied by hand), message bits per run, **git commit hash + dirty flag**, timestamp. Library versions are pinned by `uv.lock`.
- Both files are committed to git.

**Why:**
- Covers "registrar configurações, variações, número de bits, resultados brutos" and rubric item 6 (reproducibility).
- The commit hash ties every plot to the exact code that produced it; the dirty flag exposes plots made from uncommitted code before results are frozen (16/11, D19).

**Rejected:**
- *Config file (TOML/YAML) + CLI flags* — a parser and a second source of truth for an experiment that has exactly one configuration.
- *Only the CSV* — loses the burst constants and the code version, exactly what is needed to reproduce the burst curves.

## D23 — Sequential sweep; `run_link` creates the generator from the seed

**Decision:** `run_sweep.py` is a plain nested loop (scenario × line code × modulation × Eb/N0 × seed) calling `run_link(..., seed)`, printing one progress line per combination. Inside, `rng = np.random.default_rng(seed)` is created and passed to `transmit()` (D18). No parallelism unless a real run proves slow.

**Why:**
- 990 runs × tens of ms each ≈ under a minute — parallelism buys nothing.
- Keeps common random numbers (D18): the same seed gives the same noise source to every combination ⇒ lower variance in comparisons. Side effect to state on the slide: for a given seed, burst positions are identical across Eb/N0 values, so neighbouring Eb/N0 points are correlated (smoother curves); the 5 seeds remain different from each other.

**Rejected:**
- *multiprocessing* — 4–8× faster on something already under a minute, plus Windows process-startup quirks.
- *Independent streams per combination (`SeedSequence.spawn`)* — statistically purer, but discards the variance reduction: noisier comparisons for the same number of bits.

## D24 — Tests go through the contract only; each owner tests their modules

**Decision:** Tests call only the functions in `docs/interface.md`, never internals.

| Module | Tests (owner) |
|---|---|
| `source` | text → bits → text round trip; `"A"` → `01000001`; non-printable byte → `?` (P1) |
| `line_codes` | round trip for every name in `NAMES`; known vectors (Manchester `0`→`01`); injected `00`/`11` counted as violations; **inverting every chip still decodes correctly for Differential Manchester** (P1) |
| `modulation` | round trip for every name; Gray (nearest neighbours differ in 1 chip); unit average energy (P1) |
| `channel` | measured noise variance ≈ N0; fraction of time in bad state ≈ 1%; mean burst length ≈ 20; same seed ⇒ same output (P2) |
| `link` | noiseless, all 9 combinations recover the text exactly (D12) |
| theory | NRZ-BPSK BER at a few Eb/N0 values agrees with Q(√(2·Eb/N0)) within the confidence interval (P2) |

"Noiseless" needs no special mode: `ebn0_db = math.inf` ⇒ N0 = 0, and the AWGN channel adds nothing (added to the contract).

**Why:**
- Testing through the contract lets implementations change without breaking tests.
- Per-module tests localise failures — essential when two people integrate on 12/11 (D19).
- The Differential Manchester inversion test turns a slide claim (D1: immune to 180° inversion) into evidence; the theory test automates the independent check of D13.

**Rejected:**
- *Only the noiseless end-to-end test* — when it fails, nobody knows which of 5 modules broke.
- *GitHub Actions CI on every push* — cheap (~15 lines of YAML) and would help repo quality, but not chosen for now; easy to add later if integration pain appears.

## D25 — A energia usada no Eb/N0 é medida no fluxo efetivamente transmitido

**Decisão:** apesar de as constelações terem energia média unitária sob símbolos equiprováveis, o
canal calcula `Es = mean(abs(symbols)**2)` em cada transmissão. O ruído é então dimensionado por
`N0 = Es / (η × 10^(Eb/N0/10))`.

**Por quê:** os bits de um texto ASCII não são uniformes (o bit mais significativo é sempre zero).
Na 16-QAM isso faz alguns pontos aparecerem mais que outros, alterando ligeiramente a energia média
real. Medir `Es` evita que essa característica da mensagem favoreça ou prejudique uma combinação e
mantém a comparação de Eb/N0 justa. A decisão também explica por que alguns pontos aparecem pouco
nos diagramas de constelação.

## D26 — Os bits incorretos são identificados, não apenas contados

**Decisão:** `LinkResult.error_indices` guarda os índices de todos os bits da mensagem recuperados
incorretamente. `bit_errors` continua sendo a contagem e `ber = bit_errors / n_bits`.

**Por quê:** atende literalmente ao requisito de identificar os bits incorretos e permite mostrar,
no vídeo e no teste de consistência, onde as rajadas concentram erros.
