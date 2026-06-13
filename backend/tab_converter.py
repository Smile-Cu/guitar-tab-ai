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
STRING_NAMES = ["6弦(E)", "5弦(A)", "4弦(D)", "3弦(G)", "2弦(B)", "1弦(e)"]
MAX_FRET = 19


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
    将转换结果格式化为可打印的六线谱文本（调试用）

    示例输出:
    1弦(e)|--0---|
    2弦(B)|------|
    3弦(G)|--0---|
    4弦(D)|--2---|
    5弦(A)|------|
    6弦(E)|------|
    """
    if not notes:
        return ""

    lines = {}
    for s in range(1, 7):
        lines[s] = [f"{STRING_NAMES[6 - s]}|"]

    for note in notes:
        s = note.get("string")
        f = note.get("fret")
        for l in range(1, 7):
            if l == s and f is not None:
                lines[l].append(f"--{f}--")
            else:
                lines[l].append("-----")

    output = []
    for s in range(1, 7):
        output.append("".join(lines[s]) + "|")
    return "\n".join(output)



def get_mock_notes():
    """AI 未安装时使用的示例音符"""
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
        print(f"  MIDI {n['pitch']} → {n['string']}弦 {n['fret']}品")
    print()
    print("六线谱预览:")
    print(format_tab_string(tab))
