from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
import spacy

app = Flask(__name__)
nlp = spacy.load("ja_ginza")

DATA_FILE = "data.json"

def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_entries(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def parse_with_ginza(text):
    result = {
        "店舗": "",
        "品物": "",
        "支払い方法": "",
        "金額": ""
    }

    doc = nlp(text)

    # 金額（例: 250円）
    for token in doc:
        if token.text.endswith("円"):
            result["金額"] = token.text.replace("円", "").strip()
            break

    # 店舗（「で」の前）
    for i, token in enumerate(doc):
        if token.text == "で" and i > 0:
            result["店舗"] = doc[i - 1].text
            break

    # 品物（「を」の前）
    for i, token in enumerate(doc):
        if token.text == "を" and i > 0:
            result["品物"] = doc[i - 1].text
            break

    # 支払い方法
    payment_keywords = ["現金", "カード", "PayPay", "Suica"]
    for token in doc:
        if token.text in payment_keywords:
            result["支払い方法"] = token.text
            break

    return result

@app.route("/")
def index():
    entries = load_entries()
    return render_template("index.html", entries=entries)

@app.route("/add", methods=["POST"])
def add_entry():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify(success=False)

    text = data["text"]
    parsed = parse_with_ginza(text)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = {
        "datetime": now,
        "金額": parsed["金額"],
        "品物": parsed["品物"],
        "店舗": parsed["店舗"],
        "支払い方法": parsed["支払い方法"],
        "元テキスト": text
    }

    entries = load_entries()
    entries.insert(0, entry)
    save_entries(entries)
    return jsonify(success=True)

@app.route("/delete", methods=["POST"])
def delete_entry():
    data = request.get_json()
    if not data or "index" not in data:
        return jsonify(success=False)

    index = data["index"]
    entries = load_entries()
    if 0 <= index < len(entries):
        del entries[index]
        save_entries(entries)
        return jsonify(success=True)

    return jsonify(success=False)

# 🚀 Render用：ポート番号は環境変数から取得して起動！
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)