# MIDI 音符 → 吉他六线谱转换算法
# 输入: 一组 MIDI 音高（例如 [64, 67, 71]）
# 输出: 每组音高对应的 (弦号, 品位) 映射
#
# 标准吉他定弦 EADGBE（从 6 弦到 1 弦）:
#   6 弦 = E2 = MIDI 40
#   5 弦 = A2 = MIDI 45
#   4 弦 = D3 = MIDI 50
#   3 弦 = G3 = MIDI 55
#   2 弦 = B3 = MIDI 59
#   1 弦 = E4 = MIDI 64

import logging

logger = logging.getLogger(__name__)

# 标准定弦的空弦 MIDI 音高（从 6 弦到 1 弦）
STANDARD_TUNING = [40, 45, 50, 55, 59, 64]
STRING_NAMES = ["6(E)", "5(A)", "4(D)", "3(G)", "2(B)", "1(e)"]
STRING_NOTE_NAMES = ["E", "A", "D", "G", "B", "e"]
MAX_FRET = 19

# MIDI 音高 → 音名映射
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_name(pitch):
    """MIDI 音高转音名，例如 64 → E4"""
    if pitch is None:
        return "?"
    return f"{NOTE_NAMES[pitch % 12]}{pitch // 12 - 1}"


def pitch_to_tab(pitch: int):
    """
    给定一个 MIDI 音高，找到最适合的 (弦号, 品位)

    策略：遍历所有可能的 (弦号, 品位) 组合，选品位最低的那个
    （品位越低弹起来越顺手，同音高优先低把位）

    返回值：
        (string_number, fret) 或 None（音高无法演奏）
        string_number: 1-6（1 弦最细，6 弦最粗）
        fret: 0 = 空弦，1+ = 品位
    """
    best = None
    best_fret = MAX_FRET + 1

    for i in range(6):
        open_pitch = STANDARD_TUNING[i]
        string_num = 6 - i  # 转换为 1-6 的弦号
        fret = pitch - open_pitch
        if fret < 0 or fret > MAX_FRET:
            continue
        if fret < best_fret:
            best_fret = fret
            best = (string_num, fret)

    return best


def convert_notes_to_tab(notes: list[dict]):
    """
    批量转换音符列表为六线谱数据

    输入: [{"pitch": 64, "start_time": 0.5, ...}, ...]
    输出: [{"pitch": 64, "string": 1, "fret": 0, "start_time": 0.5, ...}, ...]

    防御性处理：缺少 pitch 字段的音符会被跳过并打 warn 日志
    """
    if not notes:
        return []

    result = []
    for note in notes:
        pitch = note.get("pitch")
        if pitch is None:
            logger.warning("跳过缺少 pitch 字段的音符: %s", note)
            continue

        tab_pos = pitch_to_tab(int(pitch))
        entry = dict(note)
        if tab_pos:
            entry["string"] = tab_pos[0]
            entry["fret"] = tab_pos[1]
        else:
            entry["string"] = None
            entry["fret"] = None
        result.append(entry)

    return result


def format_tab_string(notes: list[dict]) -> str:
    """
    将转换结果格式化为六线谱文本（增强版）

    特点：
    - 6 行分别对应 6 根弦
    - 音符按时间顺序从左到右排列
    - 双字符宽度对齐，品位数字右对齐
    - 空弦标记为 0
    - 无音符的位置用 -- 填充
    - 小节线用 | 分隔
    """
    if not notes:
        return ""

    # 过滤有效音符并按时间排序
    valid = [n for n in notes if n.get("string") and n.get("fret") is not None]
    if not valid:
        return "(无可演奏音符)"

    valid.sort(key=lambda n: n.get("start_time", 0))

    # 每行初始化为空链表
    lines = {s: [] for s in range(1, 7)}

    for note in valid:
        s = note["string"]
        f = note["fret"]
        fret_str = str(f)
        for l in range(1, 7):
            if l == s:
                lines[l].append(fret_str)
            else:
                lines[l].append("--")

    # 组装输出：对齐到两个字符宽度
    output = []
    for s in range(1, 7):
        label = STRING_NAMES[6 - s]
        cells = " ".join(f"{c:>2}" for c in lines[s])
        output.append(f"{label} | {cells}")

    return "\n".join(output)


def get_note_summary(notes: list[dict]) -> dict:
    """
    生成音符摘要信息，供前端展示

    返回: {"lowest_fret": 0, "highest_fret": 5, "note_count": 3, ...}
    """
    valid = [n for n in notes if n.get("string") and n.get("fret") is not None]
    if not valid:
        return {}

    frets = [n["fret"] for n in valid]
    max_f = max(frets)
    min_f = min(frets)

    return {
        "note_count": len(valid),
        "lowest_fret": min_f,
        "highest_fret": max_f,
        "used_strings": sorted(set(n["string"] for n in valid)),
        "fret_range": f"第{min_f}品 - 第{max_f}品",
        "has_open_strings": 0 in frets,
    }


def get_mock_notes():
    """AI 未安装时使用的示例音符（E 小调五声音阶基础动机）"""
    return [
        {"pitch": 40, "start_time": 0.0, "end_time": 0.5},
        {"pitch": 47, "start_time": 0.5, "end_time": 1.0},
        {"pitch": 52, "start_time": 1.0, "end_time": 1.5},
    ]


# 测试代码
if __name__ == "__main__":
    test_notes = [
        {"pitch": 40, "start_time": 0.0, "end_time": 0.5},
        {"pitch": 47, "start_time": 0.5, "end_time": 1.0},
        {"pitch": 52, "start_time": 1.0, "end_time": 1.5},
        {"pitch": 55, "start_time": 1.5, "end_time": 2.0},
        {"pitch": 59, "start_time": 2.0, "end_time": 2.5},
        {"pitch": 64, "start_time": 2.5, "end_time": 3.0},
    ]
    tab = convert_notes_to_tab(test_notes)
    print("转换结果:")
    for n in tab:
        name = midi_to_name(n.get("pitch"))
        print(f"  {name} (MIDI {n['pitch']}) → {n['string']}弦 {n['fret']}品")
    print()
    print("六线谱预览:")
    print(format_tab_string(tab))
    print()
    print("音符摘要:")
    info = get_note_summary(tab)
    for k, v in info.items():
        print(f"  {k}: {v}")
