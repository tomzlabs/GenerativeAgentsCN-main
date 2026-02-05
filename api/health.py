from flask import jsonify


def app(request):
    return jsonify({"ok": True, "service": "generative-agents-cn"})
