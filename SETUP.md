# Setup: Technique and Practice modes

## 1. Files for your GitHub repo

| File | What to do |
|---|---|
| `app.py` | Replace the old one |
| `model_answers.json` | Add (same folder as `app.py`) |
| `requirements.txt` | Replace, or add `gspread` and `google-auth` to yours |
| `config.toml` | Add inside a folder called `.streamlit` (see below) |

Your CSV stays as it is.

**Adding `config.toml`:** in GitHub, click **Add file → Create new file**, type `.streamlit/config.toml` as the name (typing the `/` creates the folder), and paste in the contents of `config.toml`. This keeps the app in light mode so the colour coding is always readable, even on devices set to dark mode.

## 2. Sending Practice results to a Google Sheet (optional)

The app works without this. Until it's set up, students can still download their answers, and the "Send to your teacher" button stays hidden.

If your Pow WOW quiz app already uses a Google service account, you can reuse it: skip to step 3 and use the same `[gcp_service_account]` block in step 4.

1. **Make the sheet.** Create a new Google Sheet, e.g. "Paper 2 Practice Results". Copy its ID from the URL: the long code between `/d/` and `/edit`.
2. **Make a service account.** In the Google Cloud Console: create a project, enable the **Google Sheets API**, create a **service account**, then under **Keys** choose **Add key → JSON**. A file downloads.
3. **Share the sheet** with the service account's email address (`client_email` in the JSON file) as **Editor**.
4. **Add the secrets in Streamlit Cloud.** Open your app's **Settings → Secrets** and paste the following, filling in the values from the JSON file:

```toml
results_sheet_id = "PASTE_THE_SHEET_ID_HERE"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"
```

Keep the `\n` characters in `private_key` exactly as they appear in the JSON file. Never put these values in GitHub itself.

The app creates two tabs in the sheet the first time a student sends results:

- **Results**: one row per attempt (name, class, paper, score, percentage, time taken, and a breakdown by question type).
- **Answers**: one row per question part (the student's answer and the mark they gave themselves), so you can check how honest their self-marking is.

## 3. Adding more model answers

Each entry in `model_answers.json` points to a question by year, month, variant, question and part, and holds the answer as paragraphs of tagged sentences:

```json
{
  "year": 2024, "month": "June", "paper": 22, "question": 3, "part": "c", "type": "analyse6",
  "model": [
    {"side": null, "sentences": [
      ["P", "The point."],
      ["E", "The first link in the chain."],
      ["E", "The next link."]
    ]}
  ]
}
```

- `type` is `analyse6`, `discuss6` or `discuss8`.
- Tags: `P` Point, `E` Explanation, `A` Application, `V` Evaluation, `C` Conclusion.
- `side` is `null` for Analyse questions, and `"for"`, `"against"` or `"conclusion"` for Discuss questions.
- Paragraphs with three or more sentences are used in **Build the chain**.

New entries appear in the app automatically after you commit the file.
