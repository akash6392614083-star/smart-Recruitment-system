from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/candidate")
def candidate():
    return render_template("candidate.html")

@app.route("/recruiter")
def recruiter():
    return render_template("recruiter.html")

if __name__ == "__main__":
    app.run(debug=True)