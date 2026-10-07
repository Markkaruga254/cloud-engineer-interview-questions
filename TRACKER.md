# Interview tracker

This fork adds a focused cloud interview study dashboard on top of the upstream question list.
`README.md` stays untouched, so upstream question updates can be merged cleanly.

## What the tracker does

- **Dashboard:** see overall interview-readiness and progress for every track.
- **Track navigation:** jump between Cloud Fundamentals, AWS, Azure, GCP and AWS services.
- **Question checklist:** check a question when you can answer it confidently in an interview.
- **Search + filters:** search a track and switch between all, unchecked and completed questions.
- **Next unchecked:** jump directly to the next question you still need to clear.
- **Notes:** keep personal interview notes beside each question.
- **Export / import:** back up or move progress between browsers.
- **Responsive layout:** works on desktop and mobile.
- **Persistent progress:** check marks and notes are stored in browser localStorage.

### Progress model

A checked question means **interview ready**. The dashboard percentage is therefore a practical readiness score, not a claim that every topic has been mastered.

Progress is stored locally in the browser and is not synced to GitHub or between devices. Use **Export progress** before changing browsers or devices.

## How it is built

- `scripts/build.py` reads `README.md` and writes `_site/index.html`.
- `site/template.html` contains the tracker UI, responsive styling and browser-side progress logic.
- `.github/workflows/pages.yml` rebuilds and deploys the site to GitHub Pages on every push to `main`.

## Preview locally

    pip install markdown
    python scripts/build.py
    python -m http.server -d _site 8000

Then open the local server in your browser.

## Pull in upstream changes

    git remote add upstream https://github.com/sv222/cloud-engineer-interview-questions.git
    git fetch upstream
    git merge upstream/main
    git push

Check marks are keyed by question text, so they survive question reordering.
