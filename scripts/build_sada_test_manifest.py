from pathlib import Path
import argparse
import csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-csv", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    by_file = {}
    with args.test_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_name = row["FileName"]
            info = by_file.setdefault(file_name, {"speakers": set()})
            speaker = row["Speaker"]
            if speaker.startswith("Speaker") and "متحدث" in speaker:
                info["speakers"].add(speaker)

    rows = []
    missing = []
    for file_name in sorted(by_file):
        wav_path = args.audio_root / file_name
        if not wav_path.exists():
            missing.append(file_name)
            continue
        recording_id = file_name.replace("/", "__").removesuffix(".wav")
        num_speakers = max(1, len(by_file[file_name]["speakers"]))
        rows.append(f"{wav_path}|{recording_id}|{num_speakers}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"saved {len(rows)} entries to {args.output}")
    if missing:
        print(f"missing_audio={len(missing)}")
        for item in missing[:20]:
            print(item)


if __name__ == "__main__":
    main()
