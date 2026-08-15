"""Use accessible, mutually exclusive tick controls in classification tables."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def add_exclusive_handler(markup: str) -> str:
    script = """
    <script>
      document.addEventListener('change', function (event) {
        const control = event.target.closest('.classification-ticks input[type="checkbox"]');
        if (!control || !control.checked) return;
        const row = control.closest('tr');
        if (!row) return;
        row.querySelectorAll('input[type="checkbox"]').forEach(function (other) {
          if (other !== control) other.checked = false;
        });
      });
    </script>
"""
    return markup.replace('    <div class="relative z-50" id="interface-container"></div>', script + '    <div class="relative z-50" id="interface-container"></div>', 1)


page46_path = ROOT / "pg046_sec001.html"
page46 = page46_path.read_text(encoding="utf-8")
page46 = page46.replace('class="section mb-8" data-section-type="activity_multiple_choice"', 'class="section mb-8 classification-ticks" data-section-type="activity_multiple_choice"', 1)
page46 = re.sub(r'\s*<div class="flex-shrink-0">\s*<div class="[^"]*option-letter[^"]*">\d+</div>\s*</div>', '', page46)
page46 = re.sub(
    r'<input type="radio" name="question-group-(\d+)"([^>]*?)class="sr-only"([^>]*)>',
    r'<input type="checkbox" data-row="\1"\2class="h-9 w-9 cursor-pointer accent-cyan-600 max-sm:h-7 max-sm:w-7"\3>',
    page46,
)
page46 = add_exclusive_handler(page46)
page46_path.write_text(page46, encoding="utf-8")

page47_path = ROOT / "pg047_sec001.html"
page47 = page47_path.read_text(encoding="utf-8")
page47 = page47.replace('class="max-w-6xl mx-auto"', 'class="max-w-6xl mx-auto classification-ticks"', 1)
page47 = re.sub(
    r'<input type="text" id="([^"]+)" aria-label="([^"]+)" data-activity-item="([^"]+)"[^>]*>',
    r'<input type="checkbox" id="\1" aria-label="\2" data-activity-item="\3" class="mx-auto block h-9 w-9 cursor-pointer accent-cyan-600 max-sm:h-7 max-sm:w-7">',
    page47,
)
page47 = page47.replace(
    '{"item-1":"ndiyo","item-2":"","item-3":"","item-4":"ndiyo","item-5":"ndiyo","item-6":"","item-7":"ndiyo","item-8":"","item-9":"","item-10":"ndiyo","item-11":"","item-12":"ndiyo"}',
    '{"item-1":true,"item-2":false,"item-3":false,"item-4":true,"item-5":true,"item-6":false,"item-7":true,"item-8":false,"item-9":false,"item-10":true,"item-11":false,"item-12":true}',
)
page47 = add_exclusive_handler(page47)
page47_path.write_text(page47, encoding="utf-8")

print("Converted pages 46–47 to mutually exclusive tick controls.")
