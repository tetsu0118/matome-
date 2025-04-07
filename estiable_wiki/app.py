from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# アップロード先ディレクトリの設定（存在しない場合は作成）
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        # articlesテーブル：タイトル、本文、画像（任意）のカラムを作成
        c.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                image TEXT
            )
        """)
        conn.commit()

@app.route("/")
def index():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, title FROM articles")
        articles = c.fetchall()
    return render_template("index.html", articles=articles)

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/survivor")
def survivor():
    return render_template("survivor.html")

@app.route("/defence")
def defence():
    return render_template("defence.html")

@app.route("/article/<int:article_id>")
def view_article(article_id):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT title, content, image FROM articles WHERE id = ?", (article_id,))
        article = c.fetchone()
    return render_template("article.html", article=article, article_id=article_id)

@app.route("/edit/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image_filename = None
        # 画像アップロードがあれば処理する
        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename:
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            if image_filename:
                # 新しい画像がアップロードされた場合、画像カラムも更新
                c.execute("UPDATE articles SET title = ?, content = ?, image = ? WHERE id = ?",
                          (title, content, image_filename, article_id))
            else:
                c.execute("UPDATE articles SET title = ?, content = ? WHERE id = ?",
                          (title, content, article_id))
            conn.commit()
        return redirect(url_for("view_article", article_id=article_id))
    
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT title, content, image FROM articles WHERE id = ?", (article_id,))
        article = c.fetchone()
    return render_template("edit.html", article=article, article_id=article_id)

@app.route("/new", methods=["GET", "POST"])
def new_article():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image_filename = None
        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename:
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO articles (title, content, image) VALUES (?, ?, ?)",
                      (title, content, image_filename))
            conn.commit()
        return redirect(url_for("index"))
    return render_template("new.html")

@app.route("/delete/<int:article_id>", methods=["POST"])
def delete_article(article_id):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM articles WHERE id = ?", (article_id,))
        conn.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
