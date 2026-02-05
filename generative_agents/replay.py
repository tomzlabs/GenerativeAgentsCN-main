import os
import json
from generative_agents.path_mapping import PERSONA_PATH_MAP
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_from_directory

FRAMES_PER_STEP = 60  # Each step contains 60 frames (sync with compress.py)
FILE_MOVEMENT = "movement.json"
PERSONAS = [
    "阿伊莎", "克劳斯", "玛丽亚", "沃尔夫冈",  # 学生
    "梅", "约翰", "埃迪",  # 家庭：教授、药店主人、学生
    "简", "汤姆",  # 家庭：家庭主妇、市场主人
    "卡门", "塔玛拉",  # 室友：供应店主人、儿童读物作家
    "亚瑟", "伊莎贝拉",  # 酒吧老板、咖啡馆老板
    "山姆", "詹妮弗",  # 家庭：退役军官、水彩画家
    "弗朗西斯科", "海莉", "拉吉夫", "拉托亚",  # 共居空间：喜剧演员、作家、画家、摄影师
    "阿比盖尔", "卡洛斯", "乔治", "瑞恩", "山本百合子", "亚当",  # 动画师、诗人、数学家、软件工程师、税务律师、哲学家
]

STATIC_ROOT = os.environ.get(
    "STATIC_ROOT",
    os.path.join(os.path.dirname(__file__), "frontend", "static"),
)

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder=STATIC_ROOT,
    static_url_path="/static",
)


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_ROOT, filename)


@app.route("/", methods=['GET'])
def index():
    name = request.args.get("name", "example")          # 记录名称
    step = int(request.args.get("step", 0))      # 回放起始步数
    speed = int(request.args.get("speed", 2))    # 回放速度（0~5）
    zoom = float(request.args.get("zoom", 0.45))  # 画面缩放比例

    if len(name) > 0:
        compressed_folder = f"results/compressed/{name}"
    else:
        return f"Invalid name of the simulation: '{name}'"

    replay_file = f"{compressed_folder}/{FILE_MOVEMENT}"
    if not os.path.exists(replay_file):
        return f"The data file doesn‘t exist: '{replay_file}'<br />Run compress.py to generate the data first."

    with open(replay_file, "r", encoding="utf-8") as f:
        params = json.load(f)

    if step < 1:
        step = 1
    if step > 1:
        # 重新设置回放的起始时间
        t = datetime.fromisoformat(params["start_datetime"])
        dt = t + timedelta(minutes=params["stride"]*(step-1))
        params["start_datetime"] = dt.isoformat()
        step = (step-1) * FRAMES_PER_STEP + 1
        if step >= len(params["all_movement"]):
            step = len(params["all_movement"])-1

        # 重新设置Agent的初始位置
        for agent in params["persona_init_pos"].keys():
            persona_init_pos = params["persona_init_pos"]
            persona_step_pos = params["all_movement"][f"{step}"]
            persona_init_pos[agent] = persona_step_pos[agent]["movement"]

    if speed < 0:
        speed = 0
    elif speed > 5:
        speed = 5
    speed = 2 ** speed

    return render_template(
        "index.html",
        persona_names=PERSONAS,
        step=step,
        play_speed=speed,
        zoom=zoom,
        persona_path_map=PERSONA_PATH_MAP,
        **params
    )


if __name__ == "__main__":
    app.run(debug=True)
