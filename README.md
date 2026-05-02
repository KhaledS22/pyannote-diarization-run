# Pyannote diarization run scripts

Run `pyannote/speaker-diarization-3.1` on:

- AppTek audio with matching RTTM files
- SADA test audio with `test.csv`

This repo is code-only. Audio, RTTM inputs, dataset CSV files, and generated outputs stay outside the repo.

## Files

- `scripts/run_pyannote_subset.py`
- `scripts/build_apptek_manifest.py`
- `scripts/build_sada_test_manifest.py`
- `scripts/run_apptek.sh`
- `scripts/run_sada_test.sh`

## Requirements

- Python 3.10+
- CUDA-enabled `torch`
- `pyannote.audio`
- `soundfile`

Install Python packages:

```bash
pip install -r requirements.txt
```

Export Hugging Face token:

```bash
export HF_TOKEN=...
```

Check CUDA:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## AppTek run

Inputs:
- `audio_root`: folder with AppTek `.wav` files
- `rttm_root`: folder with matching AppTek `.rttm` files
- `output_dir`: output folder

Command:

```bash
zsh scripts/run_apptek.sh <audio_root> <rttm_root> <output_dir>
```

Outputs:
- `<output_dir>/apptek_manifest.txt`
- `<output_dir>/rttm_outputs/*.rttm`
- `<output_dir>/rttm_outputs/summary.csv`

## SADA test run

Inputs:
- `test_csv`: SADA `test.csv`
- `audio_root`: extracted SADA test audio root
- `output_dir`: output folder

Command:

```bash
zsh scripts/run_sada_test.sh <test_csv> <audio_root> <output_dir>
```

Outputs:
- `<output_dir>/sada_test_manifest.txt`
- `<output_dir>/rttm_outputs/*.rttm`
- `<output_dir>/rttm_outputs/summary.csv`

## Notes

- AppTek and SADA inputs are not included here.
- The scripts pass `num_speakers` when it is available from the input metadata.
- SADA labels are not filtered here. Any clean scoring setup should happen later.
