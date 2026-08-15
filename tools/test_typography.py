from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
css = (ROOT / "assets/fonts.css").read_text(encoding="utf-8")

assert "font-family: 'Merriweather', serif" in css
assert "font-size: 30px" in css
assert "font-size: 60px" in css
assert "font-size: 48px" in css
assert "font-size: 36px" in css
assert "@media (max-width: 1024px)" in css
assert "@media (max-width: 640px)" in css

print("PASS: Merriweather body, question, heading, tablet and mobile typography is configured.")
