import json
import os
import requests

# --- CONFIGURATION ---
MODRINTH_USERNAME = "HypX2L"  # Change to your Modrinth username
CACHE_FILE = "last_posted_project.txt"
USER_AGENT = "MyDiscordProfileBot/1.0 (contact@example.com)"
# ---------------------

# Safely grab the webhook URL from GitHub Secrets
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def check_profile_and_post():
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
        return

    headers = {"User-Agent": USER_AGENT}
    user_url = f"https://modrinth.com{MODRINTH_USERNAME}/projects"
    response = requests.get(user_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch profile: {response.status_code}")
        return

    projects = response.json()
    if not projects:
        print("No projects found on this profile.")
        return

    # Sort to find the newest publication
    projects.sort(key=lambda x: x.get("published", ""), reverse=True)
    newest_project = projects
    project_id = newest_project["id"]
    project_slug = newest_project["slug"]
    title = newest_project["title"]
    description = newest_project.get("description", "")
    icon_url = newest_project.get("icon_url", "")

    # Check cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            if f.read().strip() == project_id:
                print("No new updates found.")
                return

    # Send message layout
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

    if webhook_res.status_code in [200, 204]:
        print(f"Successfully posted '{title}' to Discord!")
        with open(CACHE_FILE, "w") as f:
            f.write(project_id)
    else:
        print(f"Failed to post to Discord: {webhook_res.status_code}")


if __name__ == "__main__":
    check_profile_and_post()
