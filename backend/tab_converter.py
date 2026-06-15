"""
MIDI 音符 -> GTP/MIDI 文件导出 + 六线谱预览
"""

import logging

logger = logging.getLogger(__name__)

NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
STANDARD_TUNING = [40, 45, 50, 55, 59, 64]
STRING_LABELS = ["e","B","G","D","A","E"]
MAX_FRET = 19
BLOCK_SIZE = 12  # 每行 12 个音符位置后换行


def midi_to_name(pitch):
    if pitch is None: return "?"
    return f"{NOTE_NAMES[pitch % 12]}{pitch // 12 - 1}"


def create_tab_text(notes):
    if not notes: return ""

    # 音高 -> 弦号品位映射
    tab_notes = []
    for note in notes:
        pitch = note.get("pitch")
        if pitch is None: continue
        best, best_fret = None, MAX_FRET + 1
        for i in range(6):
            fret = pitch - STANDARD_TUNING[i]
            if 0 <= fret <= MAX_FRET and fret < best_fret:
                best_fret = fret
                best = (6 - i, fret)
        if best:
            tab_notes.append({"s": best[0], "f": best[1], "t": note.get("start_time", 0)})

    if not tab_notes: return ""
    tab_notes.sort(key=lambda n: n["t"])

    # 按 BLOCK_SIZE 分组
    blocks = []
    for i in range(0, len(tab_notes), BLOCK_SIZE):
        chunk = tab_notes[i:i + BLOCK_SIZE]
        lines = {s: [] for s in range(1, 7)}
        for n in chunk:
            for s in range(1, 7):
                if s == n["s"]:
                    lines[s].append(f"-{n['f']}-")
                else:
                    lines[s].append("---")

        out = []
        for s in range(1, 7):
            label = STRING_LABELS[s - 1]
            cells = "".join(lines[s])
            out.append(f"{label}|{cells}|")
        blocks.append("\n".join(out))

    return "\n\n".join(blocks)


def create_alpha_tex(notes):
    """AlphaTex (备用)"""
    if not notes: return ""
    tab_notes = []
    for note in notes:
        pitch = note.get("pitch")
        if pitch is None: continue
        best, best_fret = None, MAX_FRET + 1
        for i in range(6):
            fret = pitch - STANDARD_TUNING[i]
            if 0 <= fret <= MAX_FRET and fret < best_fret:
                best_fret = fret; best = (6 - i, fret)
        if best: tab_notes.append({"s": best[0], "f": best[1], "t": note.get("start_time", 0)})
    if not tab_notes: return ""
    tab_notes.sort(key=lambda n: n["t"])
    lines = [r"\title Tab", r"\tempo 120", "."]
    lines.append(" ".join(f"{n['s']}.{n['f']}" for n in tab_notes))
    return "\n".join(lines)


def generate_midi_file(notes, output_path):
    import pretty_midi
    midi = pretty_midi.PrettyMIDI(initial_tempo=120.0)
    prog = pretty_midi.instrument_name_to_program("Acoustic Guitar (steel)")
    inst = pretty_midi.Instrument(program=prog, name="Guitar")
    for n in notes:
        p = n.get("pitch")
        if p is None: continue
        s, e = n.get("start_time", 0), n.get("end_time", n.get("start_time", 0) + 0.5)
        inst.notes.append(pretty_midi.Note(velocity=80, pitch=int(p), start=float(s), end=float(e)))
    midi.instruments.append(inst)
    midi.write(output_path)
    return output_path


def generate_midi_from_notes(notes):
    import tempfile
    t = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
    generate_midi_file(notes, t.name)
    return t.name, "guitar_tab.mid"


def get_mock_notes():
    return [
        {"pitch": 40, "start_time": 0.0, "end_time": 0.5},
        {"pitch": 47, "start_time": 0.5, "end_time": 1.0},
        {"pitch": 52, "start_time": 1.0, "end_time": 1.5},
        {"pitch": 55, "start_time": 1.5, "end_time": 2.0},
        {"pitch": 59, "start_time": 2.0, "end_time": 2.5},
        {"pitch": 64, "start_time": 2.5, "end_time": 3.0},
        {"pitch": 64, "start_time": 3.0, "end_time": 3.5},
        {"pitch": 59, "start_time": 3.5, "end_time": 4.0},
        {"pitch": 55, "start_time": 4.0, "end_time": 4.5},
        {"pitch": 52, "start_time": 4.5, "end_time": 5.0},
        {"pitch": 47, "start_time": 5.0, "end_time": 5.5},
        {"pitch": 40, "start_time": 5.5, "end_time": 6.0},
        {"pitch": 40, "start_time": 6.0, "end_time": 6.5},
        {"pitch": 47, "start_time": 6.5, "end_time": 7.0},
        {"pitch": 52, "start_time": 7.0, "end_time": 7.5},
        {"pitch": 55, "start_time": 7.5, "end_time": 8.0},
    ]
