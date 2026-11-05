#!/usr/bin/env python3
"""Validate the n8n workflow JSON files in ./workflows.

Checks: valid JSON, required keys, unique node names, connections that point to
existing nodes, no embedded credentials, no obvious secrets.
Use --placeholders to list every YOUR_* / YOUR-* value you still need to replace.
"""
import glob, json, re, sys

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}", r"xox[abp]-[A-Za-z0-9-]{10,}", r"AKIA[0-9A-Z]{16}",
    r"ghp_[A-Za-z0-9]{30,}", r"Bearer\s+(?!YOUR_TOKEN)[A-Za-z0-9._-]{20,}",
]
PLACEHOLDER = re.compile(r"YOUR[_-][A-Za-z0-9_.-]+|yourcompany\.com")

def main(show_placeholders: bool) -> int:
    errors = 0
    files = sorted(glob.glob("workflows/*.json"))
    if not files:
        print("No workflows found"); return 1
    for f in files:
        try:
            w = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"ERROR {f}: invalid JSON ({e})"); errors += 1; continue
        raw = open(f, encoding="utf-8").read()
        for k in ("name", "nodes", "connections"):
            if k not in w:
                print(f"ERROR {f}: missing key '{k}'"); errors += 1
        names = [n["name"] for n in w.get("nodes", [])]
        if len(names) != len(set(names)):
            print(f"ERROR {f}: duplicate node names"); errors += 1
        for src, outs in w.get("connections", {}).items():
            if src not in names:
                print(f"ERROR {f}: connection source '{src}' not found"); errors += 1
            for conns in outs.values():
                for branch in conns:
                    for t in branch:
                        if t["node"] not in names:
                            print(f"ERROR {f}: '{src}' -> unknown node '{t['node']}'"); errors += 1
        for n in w.get("nodes", []):
            if "credentials" in n:
                print(f"ERROR {f}: node '{n['name']}' embeds credentials"); errors += 1
        for p in SECRET_PATTERNS:
            if re.search(p, raw):
                print(f"ERROR {f}: possible secret matching {p}"); errors += 1
        ph = sorted(set(PLACEHOLDER.findall(raw)))
        print(f"OK    {f}: {len(names)} nodes, {len(ph)} placeholders")
        if show_placeholders:
            for p in ph: print(f"        - {p}")
    print("FAILED" if errors else "All workflows valid")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main("--placeholders" in sys.argv))
