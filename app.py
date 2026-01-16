"""
Flask Blog - A simple blog for Football Manager stories
"""
from flask import Flask, render_template, abort
from datetime import datetime
import os

app = Flask(__name__)

# ============================================================
# ARTICLES DATA
# ============================================================
# Add your articles here! Each article needs:
#   - id: unique identifier (used in URL)
#   - title: display title
#   - date: publication date
#   - filename: name of the .txt file in the articles/ folder
#
# Articles are displayed newest first on the homepage.
# ============================================================

ARTICLES = [
    {
        "id": "part 1",
        "title": "How did we fall so far?",
        "date": "2024-01-15",
        "filename": "article1.txt"
    },
    {
        "id": "part 2",
        "title": "The struggle is real, or is it?",
        "date": "2024-02-20",
        "filename": "article2.txt"
    },
    {
        "id": "part 3",
        "title": "Crossing the line",
        "date": "2024-03-10",
        "filename": "article3.txt"
    },
    {
        "id": "part 4",
        "title": "Out with the old and in with the older",
        "date": "2024-04-05",
        "filename": "article4.txt"
    },
    {
        "id": "part 5",
        "title": "The Crucible",
        "date": "2024-05-12",
        "filename": "article5.txt"
    },
    {
        "id": "part 6",
        "title": "Disaster and Triumph",
        "date": "2024-06-01",
        "filename": "article6.txt"
    },
]


def get_article_content(filename):
    """Read article content from a text file."""
    filepath = os.path.join(app.root_path, "articles", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def format_date(date_string):
    """Convert date string to readable format."""
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    return date_obj.strftime("%B %d, %Y")


# Make format_date available in templates
app.jinja_env.globals["format_date"] = format_date


@app.route("/")
def home():
    """Homepage - list all articles (newest first)."""
    # Sort articles by date, newest first
    sorted_articles = sorted(ARTICLES, key=lambda x: x["date"], reverse=True)
    return render_template("index.html", articles=sorted_articles)


@app.route("/article/<article_id>")
def article(article_id):
    """Individual article page."""
    # Find the article
    article_data = None
    for a in ARTICLES:
        if a["id"] == article_id:
            article_data = a
            break

    if article_data is None:
        abort(404)

    # Get the article content
    content = get_article_content(article_data["filename"])
    if content is None:
        abort(404)

    # Convert newlines to paragraphs for display
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    return render_template(
        "article.html",
        article=article_data,
        paragraphs=paragraphs
    )


@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
