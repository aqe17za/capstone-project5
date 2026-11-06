import os

import ast

import operator

import requests

from flask import Flask, request, jsonify

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")

ROLE_SYSTEM = "system"

helpbot_prompt = os.environ.get("HELPBOT_PROMPT", "")

ALLOWED_OPS = {

    ast.Add: operator.add,

    ast.Sub: operator.sub,

    ast.Mult: operator.mul,

    ast.Div: operator.truediv,

}


def safe_calc(expression):

    def walk(node):

        if isinstance(node, ast.Expression):

            return walk(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):

            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:

            return ALLOWED_OPS[type(node.op)](walk(node.left), walk(node.right))

        raise ValueError("Only + - * / on numbers are allowed")

    return walk(ast.parse(expression, mode="eval"))


PAGE = """<!doctype html>
<html><head><title>TechCorp AI Chat</title></head>
<body style="font-family:sans-serif;max-width:800px;margin:20px auto">
<h2>TechCorp AI Chat</h2>
<div id="log"></div>
<textarea id="msg" rows="3" style="width:100%"></textarea><br>
<button onclick="send()">Send</button>
<script>

function add(who, text){

  const p = document.createElement('p');

  p.style.whiteSpace = 'pre-wrap';

  p.textContent = who + ': ' + text;

  document.getElementById('log').appendChild(p);

}

async function send(){

  const m = document.getElementById('msg').value;

  add('You', m);

  document.getElementById('msg').value = '';

  const r = await fetch('/chat', {method:'POST',

    headers:{'Content-Type':'application/json'},

    body: JSON.stringify({message: m})});

  const d = await r.json();

  add('AI', d.reply || d.error);

}
</script>
</body></html>"""


@app.route("/")

def home():

    return PAGE


@app.route("/chat", methods=["POST"])

def chat():

    user_message = request.get_json().get("message", "")

    payload = {

        "model": "llama3",

        "messages": [

            {"role": ROLE_SYSTEM, "content": helpbot_prompt},

            {"role": "user", "content": user_message},

        ],

        "stream": False,

    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=300)

    reply = r.json()["message"]["content"]

    return jsonify({"reply": reply})


@app.route("/calc", methods=["POST"])

def calc():

    expression = request.get_json().get("expression", "")

    try:

        result = safe_calc(expression)

    except (ValueError, SyntaxError, ZeroDivisionError):

        return jsonify({"error": "Invalid expression"}), 400

    return jsonify({"result": str(result)})


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=5000)
