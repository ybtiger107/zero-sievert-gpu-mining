#!/usr/bin/env python3
"""Static regression checks for the GPU Mining mod payload (no game required).

Usage: python3 tools/static_check.py
"""
import pathlib
import re
import sys

MOD = pathlib.Path(__file__).resolve().parent.parent / "mod"
errors = []


def strip(src):
    src = re.sub(r'"(?:\\.|[^"\\])*"', '""', src)
    return re.sub(r"--[^\n]*", "", src)


def func_bodies(src):
    for m in re.finditer(r"\bfunc\s*\([^)]*\)\s*\{", src):
        depth, i = 1, m.end()
        while depth and i < len(src):
            depth += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        yield src[m.end():i]


scripts = sorted(MOD.rglob("*.script"))
for path in scripts:
    code = strip(path.read_text())
    # Catspeak callbacks do not capture the script's top-level locals.
    top_level_lets = re.findall(r"^let\s+([A-Za-z_]\w*)", code, re.M)
    for body in func_bodies(code):
        for name in top_level_lets:
            if re.search(r"\b%s\b" % re.escape(name), body):
                errors.append(f"{path.name}: top-level let '{name}' used inside func")
    for a, b in (("{", "}"), ("(", ")"), ("[", "]")):
        if code.count(a) != code.count(b):
            errors.append(f"{path.name}: unbalanced {a}{b}")

init = (MOD / "init.script").read_text()
items = (MOD / "scripts" / "item.script").read_text()
rigs = (MOD / "scripts" / "rig.script").read_text()

if not re.search(r"GPU_MINING_STEP_THRESHOLD\s*=\s*162000\b", init):
    errors.append("cycle threshold is not 162000 steps")
if 'ItemSetPriceValue("btc_usb", 250000)' not in items:
    errors.append("btc_usb fixed value is not 250000")
for level in range(11):
    if f'ItemBarterCreate("miner_{level}")' not in rigs:
        errors.append(f"miner_{level} missing")
for key in ("state_version", "progress_steps", "rig_seen", "max_rig_level",
            "pending_btc", "btc_price"):
    if f'"gpu_mining_3485717804_{key}"' not in init:
        errors.append(f"canonical key {key} missing")
for legacy in ("Time BTC", "Rig level", "Rig made", "Rig has", "btc price"):
    if f'FileDataRead("{legacy}")' not in init:
        errors.append(f"legacy migration key '{legacy}' not read")
if re.search(r'ObjectSetScript\(\s*"obj_player"', init):
    errors.append("direct obj_player script override reintroduced")

for e in errors:
    print("FAIL:", e)
print(f"{len(scripts)} scripts checked, {len(errors)} failure(s)")
sys.exit(1 if errors else 0)
