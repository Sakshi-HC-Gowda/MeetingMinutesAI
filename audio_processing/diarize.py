import json
from pathlib import Path

def _save_json(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)

def _cluster_segments_by_voice(audio_path, transcript_segments, max_speakers=4):
    """
    Lightweight diarization fallback using MFCC clustering.
    Returns a list of default speaker labels (e.g., ['Speaker 1', 'Speaker 2', ...])
    aligned to transcript_segments or None if clustering failed.
    """
    try:
        import numpy as np
        import librosa
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
    except Exception:
        return None

    try:
        signal, sr = librosa.load(audio_path, sr=None, mono=True)
    except Exception:
        return None

    features = []
    segment_indices = []
    for idx, seg in enumerate(transcript_segments):
        start = max(0.0, float(seg.get("start", 0.0)))
        end = max(start + 0.05, float(seg.get("end", start + 0.05)))
        if end - start < 0.2:
            continue
        start_idx = int(start * sr)
        end_idx = int(end * sr)
        if end_idx - start_idx < int(0.2 * sr):
            continue
        snippet = signal[start_idx:end_idx]
        if not np.any(snippet):
            continue
        mfcc = librosa.feature.mfcc(y=snippet, sr=sr, n_mfcc=20)
        delta = librosa.feature.delta(mfcc)
        feat = np.concatenate(
            [
                mfcc.mean(axis=1),
                mfcc.std(axis=1),
                delta.mean(axis=1),
            ]
        )
        if np.isnan(feat).any() or np.isinf(feat).any():
            continue
        features.append(feat)
        segment_indices.append(idx)

    if len(features) < 2:
        return None

    X = np.vstack(features)
    max_k = min(max_speakers, len(features))
    best_labels = None
    best_score = -1.0
    best_k = 0

    for k in range(2, max_k + 1):
        try:
            kmeans = KMeans(n_clusters=k, n_init=10, random_state=0)
            labels = kmeans.fit_predict(X)
            if len(set(labels)) < 2:
                continue
            score = silhouette_score(X, labels)
            if score > best_score + 0.05:
                best_score = score
                best_labels = labels
                best_k = k
        except Exception:
            continue

    if best_labels is None:
        # fallback to two clusters if possible
        k = min(2, max_k)
        if k < 2:
            return None
        try:
            kmeans = KMeans(n_clusters=k, n_init=10, random_state=0)
            best_labels = kmeans.fit_predict(X)
            best_k = k
        except Exception:
            return None

    order = []
    for idx, label in zip(segment_indices, best_labels):
        if label not in order:
            order.append(label)
    label_to_name = {label: f"Speaker {i+1}" for i, label in enumerate(order)}

    defaults = [None] * len(transcript_segments)
    for idx, label in zip(segment_indices, best_labels):
        defaults[idx] = label_to_name[label]

    # Forward/backward fill gaps to maintain continuity
    last_seen = None
    for i in range(len(defaults)):
        if defaults[i] is None:
            defaults[i] = last_seen
        else:
            last_seen = defaults[i]
    last_seen = None
    for i in range(len(defaults) - 1, -1, -1):
        if defaults[i] is None:
            defaults[i] = last_seen
        else:
            last_seen = defaults[i]

    # final fallback if still None (e.g., all were None)
    defaults = [d if d else "Speaker 1" for d in defaults]
    return defaults


def diarize_audio(audio_path, transcript_segments, out_json=None, use_pyannote=True):
    """
    Attempt speaker diarization and align with transcript_segments.
    Returns list of segments with 'speaker','start','end','text'.
    Fallback: single speaker for all segments.
    """
    diarized = []
    try:
        if use_pyannote:
            from pyannote.audio import Pipeline
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
            diarization = pipeline(audio_path)
            # convert to list of (start,end, speaker_label)
            turns = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                turns.append({"start": float(turn.start), "end": float(turn.end), "speaker": speaker})
            # naive alignment: assign each transcript segment to the speaker whose turn overlaps midpoint
            for seg in transcript_segments:
                mid = (seg["start"] + seg["end"]) / 2.0
                sp = "Speaker 1"
                for t in turns:
                    if t["start"] <= mid <= t["end"]:
                        sp = t["speaker"]
                        break
                diarized.append({
                    "speaker": sp,
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                })
        else:
            raise Exception("pyannote disabled")
    except Exception:
        # lightweight heuristic fallback:
        # 1) If segment text starts with "Name: ...", use that as speaker and strip prefix
        # 2) Extract speaker names from transcript patterns
        # 3) Track unique speakers and assign them properly
        import re
        cluster_defaults = _cluster_segments_by_voice(audio_path, transcript_segments)
        alias = {}
        speakers_seen = {}  # Map speaker name to speaker label
        speaker_counter = 1
        last_speaker = None
        
        for i, seg in enumerate(transcript_segments):
            txt = (seg.get("text") or "").strip()
            sp = None
            default_label = None
            if cluster_defaults and i < len(cluster_defaults):
                default_label = cluster_defaults[i]
                sp = alias.get(default_label, default_label)
            
            # Pattern 1: "Name: content" at start of text
            m = re.match(r"^([A-Z][A-Za-z\.\- ]{1,30}):\s+(.*)$", txt)
            if m:
                sp_name = m.group(1).strip()
                txt = m.group(2).strip()
                # Normalize speaker name (remove common prefixes/suffixes)
                sp_name = re.sub(r'\s+', ' ', sp_name)
                if sp_name not in speakers_seen:
                    speakers_seen[sp_name] = sp_name
                    speaker_counter += 1
                sp = speakers_seen[sp_name]
                if default_label:
                    alias[default_label] = sp
            else:
                # Pattern 2: Look for speaker labels in brackets like [Speaker 1] or [Name]
                bracket_match = re.search(r'\[(?:Speaker\s+)?([A-Z][A-Za-z\.\- ]{1,30}|Speaker\s+\d+)\]', txt)
                if bracket_match:
                    sp_name = bracket_match.group(1).strip()
                    txt = re.sub(r'\[(?:Speaker\s+)?[A-Z][A-Za-z\.\- ]{1,30}|Speaker\s+\d+\]', '', txt).strip()
                    if sp_name not in speakers_seen:
                        speakers_seen[sp_name] = sp_name
                        speaker_counter += 1
                    sp = speakers_seen[sp_name]
                    if default_label:
                        alias[default_label] = sp
                # Pattern 3: Look for "SPEAKER_NAME:" pattern anywhere in text
                elif ':' in txt:
                    colon_parts = txt.split(':', 1)
                    potential_name = colon_parts[0].strip()
                    if len(potential_name) > 2 and len(potential_name) < 40 and re.match(r'^[A-Z][A-Za-z\.\- ]+$', potential_name):
                        sp_name = potential_name
                        txt = colon_parts[1].strip() if len(colon_parts) > 1 else txt
                        if sp_name not in speakers_seen:
                            speakers_seen[sp_name] = sp_name
                            speaker_counter += 1
                        sp = speakers_seen[sp_name]
                        if default_label:
                            alias[default_label] = sp
            
            # If no speaker found, use last speaker or default to Speaker 1
            if not sp:
                if default_label and default_label in alias:
                    sp = alias[default_label]
                elif default_label:
                    sp = default_label
                else:
                    sp = last_speaker if last_speaker else "Speaker 1"
            
            diarized.append({
                "speaker": sp,
                "start": seg.get("start"),
                "end": seg.get("end"),
                "text": txt
            })
            last_speaker = sp

    if out_json:
        _save_json(diarized, out_json)
    return diarized