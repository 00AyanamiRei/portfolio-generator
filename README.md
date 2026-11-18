# Portfolio Generator

A tiny static-site generator for developer portfolios. Edit **one file** (`profile.yaml`), push, and GitHub Actions builds and publishes your site to GitHub Pages.

**Stack:** Python 3.11+, Jinja2, PyYAML, Tailwind CSS (standalone CLI, no Node), vanilla JS (theme toggle, project filter, copy-email).

## Deploy in 3 minutes

1. **Fork** this repo (or use it as a template). For a personal site, name it `<your-username>.github.io`.
2. Edit `profile.yaml`: your name, bio, links, projects, experience, skills.
3. In the repo go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Push to `main`. The workflow in `.github/workflows/deploy.yml` builds the site and deploys it. The URL appears in the workflow summary.

## Images and CV

- Put screenshots/GIFs in `assets/images/` and reference them in `profile.yaml` (`image: "assets/images/foo.png"`).
- Put your CV at `assets/resume.pdf`.
- Missing files are skipped automatically: no broken images, no dead "Download CV" button.

## Local preview

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Download the [Tailwind standalone CLI](https://github.com/tailwindlabs/tailwindcss/releases/tag/v3.4.17) (v3.4.17) for your OS, rename it to `tailwindcss` (`tailwindcss.exe` on Windows) and put it in the repo root (it is git-ignored). Then:

```bash
python build.py
python -m http.server -d dist 8000   # open http://localhost:8000
```

Without the CLI the HTML is still generated, but `dist/styles.css` is not, so the page is unstyled.

## Structure

```
.github/workflows/deploy.yml   CI: build + deploy to GitHub Pages
assets/                        images, resume.pdf (copied to dist/assets)
src/input.css                  Tailwind entry
templates/index.html           Jinja2 template
tailwind.config.js             theme (colors, fonts, dark mode)
profile.yaml                   all content
build.py                       generator: YAML -> dist/
```

## License

MIT
