from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/jira")
def go_to_jira():
    jira_link = request.args.get("link")
    if not jira_link:
        return "Missing Jira link", 400

    # HTML meta-refresh redirect for Cloud Run
    html = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="0;url={jira_link}" />
        <title>Redirecting to Jira...</title>
      </head>
      <body>
        <p>Redirecting to Jira… If this doesn’t happen automatically,
           <a href="{jira_link}">click here</a>.</p>
      </body>
    </html>
    """
    return render_template_string(html)
