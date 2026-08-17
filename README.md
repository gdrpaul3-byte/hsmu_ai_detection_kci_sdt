# Age Differences in the Detection of AI-Generated Faces — Analysis Code

Analysis and figure-generation code for the manuscript:

> **Age Differences in the Detection of AI-Generated Faces: Sensitivity Declines While the Response Criterion Remains Unbiased**
> Sunwhi Kim (Hwasung Medi-Science University) and Sunyul Kim (Yonsei University)
> Manuscript in Korean, prepared for submission to the *Korean Journal of Cognitive and Biological Psychology* (한국심리학회지: 인지 및 생물).

The study applies signal detection theory (SDT) to a public web experiment in which 1,667 adults (ages 20–69) judged whether a single portrait was a real photograph or an AI-generated re-creation of the same identity (ChatGPT-4o or Imagen 3; yes–no task).

## Key results

- Sensitivity *d*′ declines steeply with age: **2.33 (20s) → 2.27 (30s) → 1.76 (40s) → 1.24 (50s) → 0.87 (60s)**, *F*(4, 1662) = 108.1, *p* < .001.
- The response criterion *c* stays essentially unbiased at every age: **|*c*| ≤ 0.08 in all age groups**, *F*(4, 1662) = 1.68, *p* = .153.
- The age-related decline is therefore a loss of discriminability, not a shift toward credulous responding.
- Secondary findings: the detection gap between the harder generator (ChatGPT-4o, 80.4%) and the easier one (Imagen 3, 88.9%) tends to widen with age (*r* = .15), and self-rated detection confidence tracks actual accuracy (Spearman ρ = .38).

## Contents

| File | Purpose |
|---|---|
| `analysis/kci_stats.py` | Recomputes every statistic reported in the manuscript (sample funnel, SDT indices, ANOVAs, one-sample *t* tests, generator contrast, confidence–accuracy correlations, Table 1 counts) and prints them to the console. |
| `analysis/make_kci_figures.py` | Generates the four results figures (`kci_fig1_sdt_age`, `kci_fig2_dc_plane`, `kci_fig3_generator`, `kci_fig4_confidence` = manuscript Figures 2–5) as PNG/PDF/SVG into `figures/`. |
| `analysis/make_kci_fig1_design.py` | Generates the methods figure (`kci_fig1_design` = manuscript Figure 1: mirroring procedure and trial flow). Requires three stimulus images (see below). |

Note on numbering: the figure *file* names are one off from the manuscript numbers (`kci_fig1_sdt_age` is Figure 2, etc.) because the methods figure was added last.

## Data

The scripts analyze the frozen public data release of the experiment:

- **Repository**: [gdrpaul3-byte/hsmu_ai_detection_public](https://github.com/gdrpaul3-byte/hsmu_ai_detection_public)
- **Version**: tag [`v1.0.1-sci-reports-submission`](https://github.com/gdrpaul3-byte/hsmu_ai_detection_public/releases/tag/v1.0.1-sci-reports-submission) (v1.0.1 — the frozen reference point cited by the manuscript)
- Files used: `data/exp_data/surveys_export_deidentified.csv`, `data/exp_data/responses_export_deidentified.csv`, and (for the methods figure) `stimuli/real/` and `stimuli/ai_generated/`.

No data are included here; the code reads the data repository from a fixed relative location.

## Reproduction

### 1. Install dependencies

Python 3.9+ with:

```bash
pip install -r requirements.txt
```

(`scipy`, `matplotlib`, `numpy`, `pillow`)

### 2. Arrange the directories

The scripts resolve the data by relative path (the path constants are left exactly as used for the manuscript). Clone the two repositories so they sit side by side like this, with the data repository cloned **into** `ai_detection_hsmu/human_study/`:

```
<any parent directory>/
├── hsmu_ai_detection_kci_sdt/          # this repository
│   ├── analysis/
│   └── figures/                        # created by the scripts
└── ai_detection_hsmu/
    └── human_study/                    # = clone of hsmu_ai_detection_public
        ├── data/exp_data/surveys_export_deidentified.csv
        ├── data/exp_data/responses_export_deidentified.csv
        └── stimuli/{real, ai_generated}/
```

From the parent directory:

```bash
git clone https://github.com/gdrpaul3-byte/hsmu_ai_detection_kci_sdt.git
git clone --branch v1.0.1-sci-reports-submission \
    https://github.com/gdrpaul3-byte/hsmu_ai_detection_public.git \
    ai_detection_hsmu/human_study
```

### 3. Run

From the root of this repository:

```bash
python analysis/kci_stats.py          # prints all manuscript statistics
python analysis/make_kci_figures.py   # writes results figures to figures/
```

For the methods figure, first copy the single example identity (FFHQ 01708) from the data repository into `figures/stimuli_fig1/`:

```bash
mkdir -p figures/stimuli_fig1
cp ../ai_detection_hsmu/human_study/stimuli/real/01708.png            figures/stimuli_fig1/
cp ../ai_detection_hsmu/human_study/stimuli/ai_generated/01708_chatgpt.png figures/stimuli_fig1/
cp ../ai_detection_hsmu/human_study/stimuli/ai_generated/01708_gemini.png  figures/stimuli_fig1/
```

then:

```bash
python analysis/make_kci_fig1_design.py
```

## Citation

The manuscript is not yet published; until then, please cite the preprint reporting the experiment together with this repository:

> Kim, S., & Kim, S. (2026). *Human factors in detecting AI-generated portraits: Age, sex, device, and confidence*. arXiv. https://arxiv.org/abs/2603.24048

> Kim, S., & Kim, S. (2026). *Age differences in the detection of AI-generated faces: Sensitivity declines while the response criterion remains unbiased* [Manuscript in preparation, in Korean]. Department of Bio-Healthcare, Hwasung Medi-Science University.

Data: Kim & Kim (2026), *hsmu_ai_detection_public* v1.0.1, https://github.com/gdrpaul3-byte/hsmu_ai_detection_public

## License

MIT — see [LICENSE](LICENSE).
