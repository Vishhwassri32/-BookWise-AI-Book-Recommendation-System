from flask import Flask, render_template, request, jsonify
import model

app = Flask(__name__)

@app.route("/")
def home():
    # simple landing with search box
    return render_template("index.html")

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form.get("title", "")
        results = model.recommend_by_title(query)
    return render_template("recommend.html", results=results, query=query)

@app.route("/categories")
def categories():
    summary = model.get_categories_summary()
    return render_template("categories.html", categories=summary)

@app.route("/authors", methods=["GET", "POST"])
def authors():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form.get("author", "")
        results = model.similar_authors(query)
    return render_template("authors.html", results=results, query=query)

@app.route("/trending")
def trending():
    books = model.trending_books()
    return render_template("trending.html", books=books)

@app.route("/about")
def about():
    return render_template("about.html")

# Autocomplete endpoint for AJAX
@app.route("/_suggest")
def suggest():
    q = request.args.get('q', '')
    suggestions = model.autocomplete_titles(q, limit=12)
    return jsonify(suggestions)

if __name__ == "__main__":
    app.run(debug=True)
