import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = BASE_DIR / "templates"
CONFIG_FILE = BASE_DIR / "profile.yaml"

REQUIRED_KEYS = ("meta", "hero", "projects", "experience", "education", "skills")
PLACEHOLDER_GITHUB = "https://github.com/00AyanamiRei"


def existing_or_empty(rel_path: str, label: str) -> str:
    if rel_path and not (BASE_DIR / rel_path).exists():
        print(f"[warn] {label}: '{rel_path}' not found - skipped")
        return ""
    return rel_path


CERT_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".webp")


def resolve_cert_file(rel_path: str, label: str) -> str:
    if not rel_path:
        return ""
    path = BASE_DIR / rel_path
    if path.exists():
        return rel_path
    for ext in CERT_EXTS:
        alt = path.with_suffix(ext)
        if alt.exists():
            return alt.relative_to(BASE_DIR).as_posix()
    print(f"[warn] {label}: '{rel_path}' not found - skipped")
    return ""


def render_cert_previews(certs: list) -> None:
    for c in certs:
        c["full"] = c.get("image", "")
    pdfs = [c for c in certs if c["full"].lower().endswith(".pdf")]
    if not pdfs:
        return
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("[warn] pypdfium2 is not installed - PDF previews skipped "
              "(run: uv pip install -r requirements.txt)")
        for c in pdfs:
            c["image"] = ""
        return
    out_dir = DIST_DIR / "assets" / "certificate-previews"
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in pdfs:
        src = BASE_DIR / c["full"]
        name = f"{src.stem}.webp"
        try:
            pdf = pdfium.PdfDocument(str(src))
            img = pdf[0].render(scale=2).to_pil().convert("RGB")
            img.thumbnail((900, 900))
            img.save(out_dir / name, "WEBP", quality=85)
            c["image"] = f"assets/certificate-previews/{name}"
        except Exception as exc:  # corrupted/encrypted PDF etc.
            print(f"[warn] cannot render preview for {c['full']}: {exc}")
            c["image"] = ""


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        sys.exit(f"[error] profile.yaml is missing sections: {', '.join(missing)}")
    return data


def validate(data: dict) -> None:
    hero = data["hero"]
    data["certificates"] = data.get("certificates") or []
    for c in data["certificates"]:
        c["image"] = resolve_cert_file(c.get("image", ""), f"certificate file ({c.get('title', '?')})")
        c["badge"] = existing_or_empty(c.get("badge", ""), f"badge image ({c.get('title', '?')})")
    hero["cv_pdf_path"] = existing_or_empty(hero.get("cv_pdf_path", ""), "CV")
    for p in data["projects"]:
        p["image"] = existing_or_empty(p.get("image", ""), f"image ({p['title']})")
        if p.get("github_url", "").rstrip("/") == PLACEHOLDER_GITHUB:
            print(f"[warn] '{p['title']}': github_url is a placeholder (profile root)")


def find_tailwind():
    for name in ("tailwindcss", "tailwindcss.exe"):
        local = BASE_DIR / name
        if local.exists():
            return str(local)
    return shutil.which("tailwindcss")


def build_css() -> None:
    exe = find_tailwind()
    if not exe:
        print("[warn] Tailwind standalone CLI not found - dist/styles.css NOT built "
              "(see README, 'Local preview')")
        return
    subprocess.run(
        [exe, "-c", str(BASE_DIR / "tailwind.config.js"),
         "-i", str(BASE_DIR / "src" / "input.css"),
         "-o", str(DIST_DIR / "styles.css"), "--minify"],
        check=True, cwd=BASE_DIR,
    )


def build() -> None:
    data = load_config()
    validate(data)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    if ASSETS_DIR.exists():
        shutil.copytree(ASSETS_DIR, DIST_DIR / "assets")
    render_cert_previews(data["certificates"])

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    html = env.get_template("index.html").render(**data)
    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")
    build_css()
    print(f"Successfully built portfolio into {DIST_DIR / 'index.html'}")


if __name__ == "__main__":
    build()
