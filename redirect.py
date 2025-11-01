from flask import Flask, redirect, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Redirect service running on Render!"

@app.route("/jira")
def go_to_jira():
    jira_link = request.args.get("link")
    if not jira_link:
        return "Missing Jira link", 400


    return redirect(jira_link, code=302)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

