import os
import sys

SYSTEM_PROMPT_PATTERNS = [
    “SYSTEM_PROMPT =“,
    “system_message =“,
    ‘”role”: “system”’,
]

INJECTION_PHRASES = [
    “ignore previous instructions”,
    “you are now”,
    “pretend you are”,
    “act as if you have no restrictions”,
]

PATTERNS = SYSTEM_PROMPT_PATTERNS + INJECTION_PHRASES

SELF = os.path.basename(__file__)

found = False

for root, dirs, files in os.walk(“.”):
    if “.git” in dirs:
        dirs.remove(“.git”)
    for name in files:
        if not name.endswith(“.py”):
            continue
        if name == SELF:
            continue
        path = os.path.join(root, name)
        with open(path, “r”, encoding=“utf-8”, errors=“ignore”) as f:
            for lineno, line in enumerate(f, 1):
                for pat in PATTERNS:
                    if pat.lower() in line.lower():
                        print(“[FAIL] “ + path + “:” + str(lineno) + “ matched: “ + pat)
                        found = True

if found:
    print(“Prompt-injection scanner: FAIL - hardcoded prompt or injection phrase found”)
    sys.exit(1)
else:
    print(“Prompt-injection scanner: PASS - clean”)
    sys.exit(0)
