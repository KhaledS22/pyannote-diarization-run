# Pyannote Diarization Runs

This repository contains the scripts we used to run `pyannote/speaker-diarization-3.1` on:

- AppTek audio with matching RTTM files
- SADA test audio with `test.csv`

It is code-only. Large audio files, RTTM inputs, and dataset CSV files should stay outside the repository.

## Repository structure

```text
pyannote_diarization_repo/
├── README.md
├── requirements.txt
├── .gitignore
└── scripts/
    ├── run_pyannote_subset.py
    ├── build_apptek_manifest.py
    ├── build_sada_test_manifest.py
    ├── run_apptek.sh
    └── run_sada_test.sh
```

## What each file does

- `scripts/run_pyannote_subset.py`
  Runs pyannote on a manifest file and writes RTTM outputs plus `summary.csv`.

- `scripts/build_apptek_manifest.py`
  Builds a manifest from AppTek audio and matching RTTM files.

- `scripts/build_sada_test_manifest.py`
  Builds a manifest from SADA `test.csv` and the extracted test audio.

- `scripts/run_apptek.sh`
  End-to-end run for AppTek.

- `scripts/run_sada_test.sh`
  End-to-end run for SADA test.

## What is not included

The repository does not include:

- AppTek audio files
- AppTek RTTM files
- SADA audio files
- SADA `test.csv`
- pyannote outputs
- generated manifests

## Environment

Use a Python environment with:

- Python 3.10+
- CUDA-enabled `torch`
- `pyannote.audio`
- `soundfile`

Export your Hugging Face token before running:

```bash
export HF_TOKEN=...
```

Also make sure:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

returns `True`.

## Install

Install CUDA-enabled `torch` separately for the target machine, then install:

```bash
pip install -r requirements.txt
```

## Run AppTek

Inputs needed:

- `audio_root`: folder with AppTek `.wav` files
- `rttm_root`: folder with matching AppTek `.rttm` files
- `output_dir`: where outputs should be written

Run:

```bash
zsh scripts/run_apptek.sh <audio_root> <rttm_root> <output_dir>
```

Expected outputs:

- `<output_dir>/apptek_manifest.txt`
- `<output_dir>/rttm_outputs/*.rttm`
- `<output_dir>/rttm_outputs/summary.csv`

## Run SADA test

Inputs needed:

- `test_csv`: SADA `test.csv`
- `audio_root`: extracted SADA test audio root
- `output_dir`: where outputs should be written

Run:

```bash
zsh scripts/run_sada_test.sh <test_csv> <audio_root> <output_dir>
```

Expected outputs:

- `<output_dir>/sada_test_manifest.txt`
- `<output_dir>/rttm_outputs/*.rttm`
- `<output_dir>/rttm_outputs/summary.csv`

## Notes

- The scripts pass `num_speakers` to pyannote when it is available from the input metadata.
- SADA labels are not filtered in this repository.
- Any clean scoring or special-label handling should happen later during evaluation.
