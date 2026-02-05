import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request

frames_per_step = 60

personas = [
    "阿伊莎", "克劳斯", "玛丽亚", "沃尔夫冈",
    "梅", "约翰", "埃迪",
    "简", "汤姆",
    "卡门", "塔玛拉",
    "亚瑟", "伊莎贝拉",
    "山姆", "詹妮弗",
    "弗朗西斯科", "海莉", "拉吉夫", "拉托亚",
    "阿比盖尔", "卡洛斯", "乔治", "瑞恩", "山本百合子", "亚当",
]

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
    static_url_path="/static",
)

@app.route("/", methods=['GET'])
def index():
    # Ignore name arg, always serve the demo
    step = int(request.args.get("step", 0))
    speed = int(request.args.get("speed", 2))
    zoom = float(request.args.get("zoom", 0.8))

    replay_file = "data/movement.json"
    
    if not os.path.exists(replay_file):
        # Fallback for local testing if cwd varies
        replay_file = os.path.join(os.path.dirname(__file__), "data", "movement.json")

    if not os.path.exists(replay_file):
         return f"Error: Data file not found at {replay_file}"

    with open(replay_file, "r", encoding="utf-8") as f:
        params = json.load(f)

    if step < 1:
        step = 1
    if step > 1:
        t = datetime.fromisoformat(params["start_datetime"])
        dt = t + timedelta(minutes=params["stride"]*(step-1))
        params["start_datetime"] = dt.isoformat()
        step = (step-1) * frames_per_step + 1
        if step >= len(params["all_movement"]):
            step = len(params["all_movement"])-1

        for agent in params["persona_init_pos"].keys():
            persona_init_pos = params["persona_init_pos"]
            persona_step_pos = params["all_movement"][f"{step}"]
            if agent in persona_step_pos: # Safety check
                 persona_init_pos[agent] = persona_step_pos[agent]["movement"]

    if speed < 0:
        speed = 0
    elif speed > 5:
        speed = 5
    speed = 2 ** speed

    return render_template(
        "index.html",
        persona_names=personas,
        step=step,
        play_speed=speed,
        zoom=zoom,
        **params
    )

if __name__ == "__main__":
    app.run(debug=True)
