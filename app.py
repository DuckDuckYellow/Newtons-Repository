"""
Newton's Repository - A collection of projects, stories, and experiments
"""
from flask import Flask, render_template, abort, url_for, redirect
from datetime import datetime
import os
import re

app = Flask(__name__)

BLOG_CATEGORIES = {
    "morecambe-fm26": {
        "id": "morecambe-fm26",
        "name": "Morecambe FC",
        "subtitle": "FM26 Save",
        "description": "Following Morecambe FC from administration to glory.",
        "image": "morecambe-logo.png",
        "articles": [
            {"id": "the-journey-begins", "title": "How did we fall so far?", "date": "2024-01-15", "filename": "article1.txt", "part": 1},
            {"id": "first-season-struggles", "title": "The struggle is real, or is it?", "date": "2024-02-20", "filename": "article2.txt", "part": 2},
            {"id": "transfer-window-rebuild", "title": "Crossing the line", "date": "2024-03-10", "filename": "article3.txt", "part": 3},
            {"id": "turning-point", "title": "Out with the old and in with the older", "date": "2024-04-05", "filename": "article4.txt", "part": 4},
            {"id": "promotion-push", "title": "The Crucible", "date": "2024-05-12", "filename": "article5.txt", "part": 5},
            {"id": "glory-day", "title": "Disaster and Triumph", "date": "2024-06-01", "filename": "article6.txt", "part": 6},
        ]
    }
}

PROJECTS = [
    {"id": "meal-generator", "name": "Meal Generator", "description": "A tool to help plan weekly meals.", "status": "planned"},
    {"id": "fm-tools", "name": "FM Analytics Tools", "description": "Utilities for analyzing FM save data.", "status": "planned"},
]

def get_article_content(filename):
    filepath = os.path.join(app.root_path, "articles", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

def format_date(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    return date_obj.strftime("%B %d, %Y")

def calculate_reading_time(text):
    words = len(text.split())
    return max(1, round(words / 200))

def get_excerpt(text, sentence_count=2):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    excerpt = ' '.join(sentences[:sentence_count])
    if len(excerpt) > 200:
        excerpt = excerpt[:197] + '...'
    return excerpt

def parse_content(text):
    blocks = []
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        is_heading = re.match(r'^Part\s+\d+', para, re.IGNORECASE) or (len(para) < 80 and not para.endswith('.'))
        blocks.append({"type": "heading" if is_heading else "paragraph", "content": para})
    return blocks

def get_category_articles(category_id):
    category = BLOG_CATEGORIES.get(category_id)
    if not category:
        return None, []
    articles = []
    for article in category["articles"]:
        content = get_article_content(article["filename"])
        articles.append({**article, "reading_time": calculate_reading_time(content) if content else 0, "excerpt": get_excerpt(content) if content else "", "category_id": category_id})
    return category, sorted(articles, key=lambda x: x["part"])

def get_article_by_id(category_id, article_id):
    category = BLOG_CATEGORIES.get(category_id)
    if not category:
        return None, None
    for article in category["articles"]:
        if article["id"] == article_id:
            return category, article
    return category, None

def get_prev_next_articles(category_id, current_part):
    category = BLOG_CATEGORIES.get(category_id)
    if not category:
        return None, None
    prev_article, next_article = None, None
    for article in category["articles"]:
        if article["part"] == current_part - 1:
            prev_article = article
        elif article["part"] == current_part + 1:
            next_article = article
    return prev_article, next_article

def get_latest_article():
    latest, latest_date, latest_category = None, None, None
    for cat_id, category in BLOG_CATEGORIES.items():
        for article in category["articles"]:
            article_date = datetime.strptime(article["date"], "%Y-%m-%d")
            if latest_date is None or article_date > latest_date:
                latest, latest_date, latest_category = article, article_date, category
    if latest and latest_category:
        content = get_article_content(latest["filename"])
        return {**latest, "category_id": latest_category["id"], "category_name": latest_category["name"], "excerpt": get_excerpt(content) if content else "", "reading_time": calculate_reading_time(content) if content else 0}
    return None

app.jinja_env.globals["format_date"] = format_date

@app.route("/")
def home():
    return render_template("index.html", latest_article=get_latest_article(), categories=BLOG_CATEGORIES, projects=PROJECTS)

@app.route("/blog")
def blog_home():
    categories = [{**cat, "article_count": len(cat["articles"])} for cat_id, cat in BLOG_CATEGORIES.items()]
    return render_template("blog_home.html", categories=categories)

@app.route("/blog/<category_id>")
def blog_category(category_id):
    category, articles = get_category_articles(category_id)
    if not category:
        abort(404)
    return render_template("blog_category.html", category=category, articles=articles, total_parts=len(articles))

@app.route("/blog/<category_id>/<article_id>")
def article(category_id, article_id):
    category, article_data = get_article_by_id(category_id, article_id)
    if not category or not article_data:
        abort(404)
    content = get_article_content(article_data["filename"])
    if not content:
        abort(404)
    prev_article, next_article = get_prev_next_articles(category_id, article_data["part"])
    return render_template("article.html", article=article_data, category=category, content_blocks=parse_content(content), reading_time=calculate_reading_time(content), prev_article=prev_article, next_article=next_article, total_parts=len(category["articles"]))

@app.route("/article/<article_id>")
def article_legacy(article_id):
    for cat_id, category in BLOG_CATEGORIES.items():
        for article in category["articles"]:
            if article["id"] == article_id:
                return redirect(url_for('article', category_id=cat_id, article_id=article_id))
    abort(404)

@app.route("/projects")
def projects():
    return render_template("projects.html", projects=PROJECTS)

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
