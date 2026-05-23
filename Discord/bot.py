import json
import os
import requests

# --- CONFIGURATION ---
MODRINTH_USERNAME = "HypX2L"  
CACHE_FILE = "Discord/last_posted_project.txt"
USER_AGENT = "MyDiscordProfileBot/1.0 (contact@example.com)"
# ---------------------

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check_profile_and_post():
    # Verify if your webhook secret is properly fetched
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL.strip() == "":
        print("❌ CRITICAL ERROR: DISCORD_WEBHOOK_URL is missing in GitHub Secrets!")
        return

    headers = {"User-Agent": USER_AGENT}
    user_url = f"https://modrinth.com{MODRINTH_USERNAME}/projects"
    response = requests.get(user_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch Modrinth profile. Status code: {response.status_code}")
        return

    projects = response.json()
    if not projects:
        print("ℹ️ No projects found on this profile yet.")
        return

    # Filter/Sort to grab the newest project
    projects.sort(key=lambda x: x.get("published", ""), reverse=True)
    newest_project = projects

    project_id = newest_project["id"]
    project_slug = newest_project["slug"]
    title = newest_project["title"]
    description = newest_project.get("description", "")
    icon_url = newest_project.get("icon_url", "")

    # Cache handling logic
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            if f.read().strip() == project_id:
                print("✅ No brand-new packs found. Everything is up to date!")
                return

    payload = {
        "embeds": [
            {
                "title": f"🆕 New Texture Pack Published: {title}",
                "url": f"https://modrinth.com{project_slug}",
                "description": f"**Description:**\n{description[:1000]}",
                "color": 5814783,
                "thumbnail": {"url": icon_url} if icon_url else {},
                "footer": {"text": f"Uploaded by {MODRINTH_USERNAME}"},
            }
        ]
    }

    webhook_res = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    # FIXED: Check array container elements safely
    if webhook_res.status_code in [200, 204]:
        print(f"🚀 Success! Posted '{title}' to Discord.")
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            f.write(project_id)
    else:
        print(f"❌ Discord API error code: {webhook_res.status_code}")
        print(webhook_res.text)

if __name__ == "__main__":
    check_profile_and_post()
