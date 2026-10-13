"""Tek komutla kontrol: stil düzeltme + statik analiz + testler + görev durumu.

Kullanım (proje klasöründe, sanal ortam aktifken):
    python scripts/check.py

GitHub Actions özet tablosu için:
    python scripts/check.py --summary
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
PENDING = re.compile(r'^pytestmark = pytest\.mark\.xfail\(.*reason="(T\d+\.\d+)', re.MULTILINE)
# Test dosyasının ilk satırı: """T1.2 — Kısa başlık (fonksiyon_adi). Ek açıklama...
TASK_IN_DOCSTRING = re.compile(r'^"""(T\d+\.\d+) — (.*?)(?:\. |\.?"""|\.?\n)', re.MULTILINE)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def task_status() -> list[tuple[str, str, bool, str]]:
    """(görev, açıklama, bitti_mi, test_dosyası) listesi — test dosyalarından okunur."""
    rows = []
    for path in sorted(TESTS.rglob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        header = TASK_IN_DOCSTRING.search(text)
        if not header:
            continue
        task, title = header.groups()
        rows.append((task, title.strip(), PENDING.search(text) is None, str(path.relative_to(ROOT))))
    return sorted(rows, key=lambda row: [int(part) for part in row[0][1:].split(".")])


def run(title: str, *args: str) -> int:
    print(f"\n=== {title} ===", flush=True)
    return subprocess.call([sys.executable, "-m", *args], cwd=ROOT)


def print_tasks() -> None:
    print("\n=== Görev durumu ===")
    for task, title, done, path in task_status():
        print(f"  {'✅' if done else '⏳'} {task:<5} {title:<45} {path}")


def print_summary_markdown() -> None:
    rows = task_status()
    done = sum(1 for row in rows if row[2])
    print(f"### Görev durumu: {done}/{len(rows)} tamam\n")
    print("| Görev | Açıklama | Durum | Test dosyası |")
    print("|---|---|---|---|")
    for task, title, is_done, path in rows:
        print(f"| {task} | {title} | {'✅ tamam' if is_done else '⏳ bekliyor'} | `{path}` |")
    log = ROOT / "pytest.log"
    if log.exists():
        lines = [line for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            print(f"\n**pytest:** `{lines[-1].strip('= ')}`")


def main() -> int:
    if "--summary" in sys.argv:
        print_summary_markdown()
        return 0

    run("1/4 Stil düzeltme (ruff --fix)", "ruff", "check", "--fix", "--quiet", ".")
    run("2/4 Biçimlendirme (ruff format)", "ruff", "format", "--quiet", ".")
    lint_rc = run("3/4 Statik analiz (ruff check)", "ruff", "check", ".")
    test_rc = run("4/4 Testler (pytest)", "pytest", "-q")
    print_tasks()

    print("\n=== Sonuç ===")
    if lint_rc == 0 and test_rc == 0:
        print("HER ŞEY TAMAM ✅  Şimdi commit + push yapabilirsin.")
        return 0
    if lint_rc:
        print("❌ Ruff otomatik düzeltemediği bir sorun buldu: yukarıdaki dosya:satır mesajına bak.")
    if test_rc:
        print("❌ Testlerde sorun var. Yukarıdaki pytest çıktısında aradığın kelimeye göre:")
        print("   XPASS(strict)        -> Görev bitmiş! Test dosyasındaki 'pytestmark = ...' satırını sil.")
        print("   FAILED ... assert    -> Kodun sonucu testin beklediğinden farklı; 'assert' satırını oku.")
        print("   NotImplementedError  -> Fonksiyon henüz yazılmamış ('raise NotImplementedError' duruyor).")
        print("   ImportError / AttributeError -> İsim sözleşmeyle aynı değil (docs/TEST_STRATEGY.md).")
        print("   ModuleNotFoundError  -> Sanal ortam aktif değil ya da paketler kurulu değil (README).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
