"""
web_builder.py
--------------
Lets Geronimo build a website (by asking Gemini to generate the HTML),
preview it locally, and publish it live to GitHub Pages.

One-time setup needed before publishing works — see README.md.
"""

import os
import subprocess
import webbrowser

from google import genai

# Anchored to THIS file's own folder, not to wherever the app happens to be
# launched from - so it finds the website folder no matter how Geronimo was
# started (double-click, shortcut, Startup folder, etc).
APP_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_DIR = os.path.join(APP_DIR, "website")
INDEX_FILE = os.path.join(WEBSITE_DIR, "index.html")
MODEL = "gemini-3.8-flash"

_web_client = None


def _get_web_client():
    global _web_client
    if _web_client is None:
        _web_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _web_client


def _strip_code_fences(text: str) -> str:
    """Gemini sometimes wraps code in ``` fences — remove them if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def build_website(description: str) -> str:
    """Create a brand-new website from scratch based on a description.

    Args:
        description: What the website should be about and look like,
            e.g. "a one-page portfolio site for a photographer, dark theme".
    """
    os.makedirs(WEBSITE_DIR, exist_ok=True)
    client = _get_web_client()
    prompt = (
        "Create a complete, self-contained single HTML file for a website. "
        "Put all CSS inside a <style> tag in the <head> — no external files. "
        "Make it visually polished and modern. "
        "Return ONLY the raw HTML, with no explanation and no markdown code fences.\n\n"
        f"Website description: {description}"
    )
    response = client.models.generate_content(model=MODEL, contents=prompt)
    html = _strip_code_fences(response.text)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    return (
        "I've built the website and saved it. "
        "Want me to show you a preview, or publish it live?"
    )


def update_website(instructions: str) -> str:
    """Change or add to the existing website's content or design.

    Args:
        instructions: What to change, e.g. "add a contact section" or
            "make the background dark blue".
    """
    if not os.path.exists(INDEX_FILE):
        return _missing_website_message()

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        current_html = f.read()

    client = _get_web_client()
    prompt = (
        "Here is the current HTML of a website:\n\n"
        f"{current_html}\n\n"
        f"Apply this change: {instructions}\n\n"
        "Return the FULL updated HTML file, with no explanation and no markdown code fences."
    )
    response = client.models.generate_content(model=MODEL, contents=prompt)
    html = _strip_code_fences(response.text)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    return "I've updated the website. Want me to publish the changes live?"


def _missing_website_message() -> str:
    """A specific, debuggable message showing exactly where we looked."""
    if os.path.isdir(WEBSITE_DIR):
        try:
            found = os.listdir(WEBSITE_DIR)
        except OSError:
            found = None
        if found:
            return (
                f"I looked for {INDEX_FILE} but it's not there. "
                f"The website folder ({WEBSITE_DIR}) has these files instead: {', '.join(found)}. "
                "If your site's main file has a different name, rename it to index.html."
            )
        return f"The website folder exists ({WEBSITE_DIR}) but it's empty. Ask me to build a website first."
    return f"There's no website built yet. I looked for one at {WEBSITE_DIR}, ask me to build one first."


def preview_website_locally() -> str:
    """Open the current version of the website in the browser, without publishing it."""
    if not os.path.exists(INDEX_FILE):
        return _missing_website_message()
    webbrowser.open("file://" + os.path.abspath(INDEX_FILE))
    return "Opened a preview of the website in your browser."


def publish_website() -> str:
    """Publish the current website live to the internet via GitHub Pages."""
    token = os.environ.get("GITHUB_TOKEN")
    username = os.environ.get("GITHUB_USERNAME")
    repo = os.environ.get("GITHUB_REPO")

    if not (token and username and repo):
        return (
            "GitHub isn't set up yet. GITHUB_TOKEN, GITHUB_USERNAME and "
            "GITHUB_REPO need to be set as environment variables first — "
            "see the README for how."
        )
    if not os.path.exists(INDEX_FILE):
        return _missing_website_message()

    remote_url = f"https://{username}:{token}@github.com/{username}/{repo}.git"

    def run(cmd):
        return subprocess.run(
            cmd, cwd=WEBSITE_DIR, shell=True, capture_output=True, text=True
        )

    if not os.path.exists(os.path.join(WEBSITE_DIR, ".git")):
        run("git init")
        run("git branch -M main")

    run("git remote remove origin")  # ignore error if it doesn't exist yet
    run(f"git remote add origin {remote_url}")
    run("git add .")
    run('git commit -m "Update website"')
    result = run("git push -u origin main --force")

    if result.returncode != 0:
        return (
            "Something went wrong while publishing. "
            f"Details: {result.stderr.strip()[-400:]}"
        )

    live_url = f"https://{username}.github.io/{repo}/"
    return f"Published! It should be live in a minute or two at {live_url}"
