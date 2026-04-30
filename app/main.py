from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.assignments import load_assignments
from app.routes.reinvite import router as reinvite_router

app = FastAPI(title="GitHub Classroom Reinvite Tool")
app.include_router(reinvite_router)


@app.get("/", response_class=HTMLResponse)
def index():
    assignment_options = "\n".join(
        f'<option value="{assignment}">{assignment}</option>'
        for assignment in load_assignments()
    )

    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>GitHub Classroom Reinvite Tool</title>
        <style>
          body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 720px;
            margin: 3rem auto;
            padding: 0 1rem;
            line-height: 1.5;
          }}
          form {{
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 1.5rem;
            background: #fafafa;
          }}
          label {{ font-weight: 650; }}
          input, select, button {{
            width: 100%;
            padding: 0.75rem;
            margin-top: 0.35rem;
            margin-bottom: 1rem;
            font-size: 1rem;
          }}
          button {{ cursor: pointer; font-weight: 700; }}
          #result {{ margin-top: 1rem; }}
        </style>
      </head>
      <body>
        <h1>GitHub Classroom Reinvite Tool</h1>
        <p>Use this form to restore write access to your GitHub Classroom repository.</p>

        <form id="reinvite-form">
          <label for="username">GitHub username</label>
          <input id="username" name="username" required placeholder="octocat" />

          <label for="assignment">Assignment</label>
          <select id="assignment" name="assignment" required>
            {assignment_options}
          </select>

          <button type="submit">Request access</button>
        </form>

        <div id="result"></div>

        <script>
          const form = document.getElementById("reinvite-form");
          const result = document.getElementById("result");

          form.addEventListener("submit", async (event) => {{
            event.preventDefault();
            result.textContent = "Submitting...";

            const payload = {{
              username: form.username.value,
              assignment: form.assignment.value
            }};

            const response = await fetch("/api/reinvite", {{
              method: "POST",
              headers: {{ "Content-Type": "application/json" }},
              body: JSON.stringify(payload)
            }});

            const data = await response.json();

            if (response.ok) {{
              result.innerHTML = `<strong>Success:</strong> ${{data.status}} for <code>${{data.repo}}</code>.`;
            }} else {{
              result.innerHTML = `<strong>Error:</strong> ${{JSON.stringify(data.detail)}}`;
            }}
          }});
        </script>
      </body>
    </html>
    """
