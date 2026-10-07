# Interview tracker

This fork adds a checklist site on top of the upstream question list.
`README.md` is untouched, so upstream changes merge cleanly.

- `scripts/build.py` reads `README.md` and writes `_site/index.html`
- `site/template.html` is the page (layout, styles, checkbox logic)
- `.github/workflows/pages.yml` rebuilds and deploys on every push to `main`

## Preview locally

    pip install markdown
    python scripts/build.py
    python -m http.server -d _site 8000

## Pull in upstream changes

    git remote add upstream https://github.com/sv222/cloud-engineer-interview-questions.git
    git fetch upstream
    git merge upstream/main
    git push

Check marks are keyed by question text, so they survive reordering.
They live in the browser's localStorage: use Export progress to back them up
or move them to another browser.
