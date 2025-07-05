import json
import os

def load_grades(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_grades(filename, grades):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(grades, f, ensure_ascii=False, indent=2)

def diff_grades(old, new):
    changed = []
    for ders, notu in new.items():
        if ders not in old or old[ders] != notu:
            changed.append((ders, notu))
    return changed
