from pathlib import Path
import argparse


def count_speakers(rttm_path: Path) -> int:
    speakers = set()
    for line in rttm_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0] == "SPEAKER":
            speakers.add(parts[7])
    return len(speakers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--rttm-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    audio_by_stem = {p.stem: p for p in args.audio_root.glob("*.wav")}
    rows = []
    for rttm_path in sorted(args.rttm_root.glob("*.rttm")):
        stem = rttm_path.stem
        wav_path = audio_by_stem.get(stem)
        if wav_path is None:
            continue
        num_speakers = count_speakers(rttm_path)
        rows.append(f"{wav_path}|{stem}|{num_speakers}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"saved {len(rows)} entries to {args.output}")


if __name__ == "__main__":
    main()
