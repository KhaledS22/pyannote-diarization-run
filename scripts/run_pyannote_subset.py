from pathlib import Path
import argparse
import csv
import os
import wave

import soundfile as sf
import torch
from pyannote.audio import Pipeline


def load_pipeline(model_id: str, token: str | None):
    if token:
        try:
            return Pipeline.from_pretrained(model_id, token=token)
        except TypeError:
            return Pipeline.from_pretrained(model_id, use_auth_token=token)
    return Pipeline.from_pretrained(model_id)


def duration_seconds(audio_path: Path) -> float:
    with wave.open(str(audio_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def num_hyp_speakers(diarization) -> int:
    speakers = set()
    for _, _, speaker in iter_tracks(diarization):
        speakers.add(str(speaker))
    return len(speakers)


def get_annotation(diarization):
    if hasattr(diarization, "write_rttm"):
        return diarization
    if hasattr(diarization, "to_annotation"):
        return diarization.to_annotation()
    for name in ("diarization", "annotation", "_diarization", "_annotation"):
        if hasattr(diarization, name):
            return getattr(diarization, name)
    if isinstance(diarization, dict):
        if "diarization" in diarization:
            return diarization["diarization"]
        if "annotation" in diarization:
            return diarization["annotation"]
    for name in dir(diarization):
        if "annotation" in name or "diarization" in name:
            try:
                val = getattr(diarization, name)
            except Exception:
                continue
            if hasattr(val, "write_rttm") or hasattr(val, "itertracks"):
                return val
    return None


def iter_tracks(diarization):
    ann = get_annotation(diarization)
    if ann is not None and hasattr(ann, "itertracks"):
        return ann.itertracks(yield_label=True)
    if hasattr(diarization, "itertracks"):
        return diarization.itertracks(yield_label=True)
    raise TypeError("Diarization output does not support itertracks.")


def write_rttm(diarization, output_path: Path, recording_id: str) -> None:
    ann = get_annotation(diarization)
    with output_path.open("w", encoding="utf-8") as f:
        if ann is not None and hasattr(ann, "write_rttm"):
            ann.write_rttm(f)
            return
        if hasattr(diarization, "to_rttm"):
            f.write(diarization.to_rttm())
            return
        for turn, _, speaker in iter_tracks(diarization):
            start = float(turn.start)
            dur = max(0.0, float(turn.end) - start)
            f.write(
                f"SPEAKER {recording_id} 1 {start:.3f} {dur:.3f} <NA> <NA> {speaker} <NA> <NA>\n"
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-file", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--model-id", default="pyannote/speaker-diarization-3.1")
    ap.add_argument("--default-num-speakers", type=int, default=None)
    args = ap.parse_args()

    token = os.getenv("HF_TOKEN")
    pipeline = load_pipeline(args.model_id, token)
    device = torch.device(args.device)
    pipeline.to(device)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_dir / "summary.csv"

    rows = []
    entries = []
    with args.list_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            audio_path = Path(parts[0])
            recording_id = parts[1] if len(parts) > 1 and parts[1] else audio_path.stem
            num_speakers = None
            if len(parts) > 2 and parts[2]:
                num_speakers = int(parts[2])
            elif args.default_num_speakers is not None:
                num_speakers = args.default_num_speakers
            entries.append((audio_path, recording_id, num_speakers))

    for index, (audio_path, recording_id, num_speakers) in enumerate(entries, 1):
        if not audio_path.exists():
            rows.append(
                {
                    "recording_id": recording_id,
                    "audio_path": str(audio_path),
                    "status": "missing_audio",
                    "audio_sec": "",
                    "hyp_speakers": "",
                    "num_speakers_arg": num_speakers if num_speakers is not None else "",
                    "rttm_path": "",
                }
            )
            continue

        waveform, sample_rate = sf.read(str(audio_path))
        if waveform.ndim == 1:
            waveform = waveform[None, :]
        else:
            waveform = waveform.T

        kwargs = {}
        if num_speakers is not None:
            kwargs["num_speakers"] = num_speakers

        print(f"[{index}/{len(entries)}] {recording_id}", flush=True)
        diarization = pipeline({"waveform": torch.tensor(waveform, dtype=torch.float32), "sample_rate": sample_rate}, **kwargs)
        rttm_path = args.out_dir / f"{recording_id}.rttm"
        write_rttm(diarization, rttm_path, recording_id)
        rows.append(
            {
                "recording_id": recording_id,
                "audio_path": str(audio_path),
                "status": "ok",
                "audio_sec": f"{duration_seconds(audio_path):.2f}",
                "hyp_speakers": num_hyp_speakers(diarization),
                "num_speakers_arg": num_speakers if num_speakers is not None else "",
                "rttm_path": str(rttm_path),
            }
        )

    with summary_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "recording_id",
                "audio_path",
                "status",
                "audio_sec",
                "hyp_speakers",
                "num_speakers_arg",
                "rttm_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved summary to {summary_path}", flush=True)


if __name__ == "__main__":
    main()
