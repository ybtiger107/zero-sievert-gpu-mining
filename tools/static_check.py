#!/usr/bin/env python3
"""Static regression checks for ZERO Sievert mod payloads (no game required).

Usage: python3 tools/static_check.py [mod_dir]

Without an argument the GPU Mining payload is checked, including its gameplay
invariants. With a mod directory only the generic Mod API 3 checks run.

These are string-level checks. They reject known failure patterns; they do
not prove Catspeak runtime behavior.
"""
import pathlib
import re
import sys

DEFAULT_MOD = pathlib.Path(__file__).resolve().parent.parent / "mod"
MOD = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_MOD
GPU_MINING = MOD == DEFAULT_MOD
EXPOSE_PREFIX = "GpuMining3485717804"
errors = []

IDENT = r"[A-Za-z_]\w*"


def strip(src):
    src = re.sub(r'@?"(?:\\.|[^"\\])*"', '""', src)
    return re.sub(r"--[^\n]*", "", src)


def func_spans(src):
    """Yield (params, body_start, body_end) for every func, outermost first."""
    for m in re.finditer(r"\bfunc\s*\(([^)]*)\)\s*\{", src):
        depth, i = 1, m.end()
        while depth and i < len(src):
            depth += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        yield m.group(1), m.end(), i - 1


def top_level_text(src):
    """Source with every function body blanked out."""
    out, last = [], 0
    for _, start, end in sorted(func_spans(src), key=lambda s: s[1]):
        if start < last:
            continue
        out.append(src[last:start])
        last = end
    out.append(src[last:])
    return "".join(out)


scripts = sorted(MOD.rglob("*.script"))
codes = {path: strip(path.read_text(errors="replace")) for path in scripts}

for path, code in codes.items():
    name = path.relative_to(MOD)
    for a, b in (("{", "}"), ("(", ")"), ("[", "]")):
        if code.count(a) != code.count(b):
            errors.append(f"{name}: unbalanced {a}{b}")

    # Mod API 3: a function given to an event, object script, timer or
    # ScriptExpose cannot rely on variables defined outside itself. Reject
    # any top-level binding (let or plain assignment) used inside a func.
    top = top_level_text(code)
    top_names = set(re.findall(rf"^\s*(?:let\s+)?({IDENT})\s*(?:[-+*/]?=)(?!=)", top, re.M))
    for params, start, end in func_spans(code):
        body = code[start:end]
        local = set(re.findall(IDENT, params))
        local |= set(re.findall(rf"\blet\s+({IDENT})", body))
        for inner_params, _, _ in func_spans(body):
            local |= set(re.findall(IDENT, inner_params))
        for top_name in sorted(top_names - local):
            if re.search(rf"(?<![\w.]){re.escape(top_name)}\b", body):
                errors.append(f"{name}: top-level '{top_name}' used inside func")

# ScriptGet names must be exposed by this mod or be one of its script files.
# A ScriptGet outside any func runs immediately, so its ScriptExpose must
# come earlier in the same file.
raw = "\n".join(p.read_text(errors="replace") for p in scripts)
exposed = re.findall(r'ScriptExpose\(\s*"([^"]+)"', raw)
script_files = {str(p.relative_to(MOD)) for p in scripts} | {p.name for p in scripts}
for path in scripts:
    text = path.read_text(errors="replace")
    blanked = top_level_text(re.sub(r"--[^\n]*", "", text))
    for m in re.finditer(r'ScriptGet\(\s*"([^"]+)"', blanked):
        expose = re.search(r'ScriptExpose\(\s*"%s"' % re.escape(m.group(1)), text)
        if expose and expose.start() > m.start():
            errors.append(f"{path.name}: ScriptGet('{m.group(1)}') runs before its ScriptExpose")
for wanted in re.findall(r'ScriptGet\(\s*"([^"]+)"', raw):
    if wanted not in exposed and wanted not in script_files:
        errors.append(f"ScriptGet('{wanted}') has no matching ScriptExpose")
if GPU_MINING:
    for name in re.findall(r'ScriptExpose\(\s*"([^"]+)"', raw):
        if not name.startswith(EXPOSE_PREFIX):
            errors.append(f"ScriptExpose name '{name}' is not namespaced")

# Mod API 3: NpcCopy's destination ID must be new, so it must not follow
# NpcCreate of the same ID.
created = set(re.findall(r'NpcCreate\(\s*"([^"]+)"', raw))
for dest in re.findall(r'NpcCopy\(\s*"([^"]+)"', raw):
    if dest in created:
        errors.append(f"NpcCopy destination '{dest}' was already created by NpcCreate")

if GPU_MINING:
    init = (MOD / "init.script").read_text()
    items = (MOD / "scripts" / "item.script").read_text()
    rigs = (MOD / "scripts" / "rig.script").read_text()

    for needle in ("Clamp(progress_steps + 1, 0, 162000)", "progress_steps >= 162000",
                   "progress_steps < 162000"):
        if needle not in init:
            errors.append(f"cycle threshold check missing: {needle}")
    if "RandomRange(100000, 400000)" not in init:
        errors.append("BTC settlement price range is not 100000..400000")
    if 'ItemSetPriceValue("btc_usb", 250000)' not in items:
        errors.append("btc_usb fixed value is not 250000")
    for level in range(11):
        if f'ItemBarterCreate("miner_{level}")' not in rigs:
            errors.append(f"miner_{level} missing")
    for key in ("state_version", "progress_steps", "rig_seen", "max_rig_level",
                "pending_btc", "btc_price"):
        if f'"gpu_mining_3485717804_{key}"' not in init:
            errors.append(f"canonical key {key} missing")
    if 'FileDataWrite("gpu_mining_3485717804_state_version", 1)' not in init:
        errors.append("migration version 1 not written")
    for legacy in ("Time BTC", "Rig level", "Rig made", "Rig has", "btc price"):
        if f'FileDataRead("{legacy}")' not in init:
            errors.append(f"legacy migration key '{legacy}' not read")
    if re.search(r'ObjectSetScript\(\s*"obj_player"', init):
        errors.append("direct obj_player script override reintroduced")

for e in errors:
    print("FAIL:", e)
print(f"{MOD}: {len(scripts)} scripts checked, {len(errors)} failure(s)")
sys.exit(1 if errors else 0)
