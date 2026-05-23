import os
import sys
import requests

# Configuration
MODRINTH_ID = "HypX2L"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
STATE_FILE = "last_project.txt"

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
    sys.exit(1)

def get_latest_resource_pack():
    # Modrinth API endpoint to get user's projects
    url = f"https://api.modrinth.com/v2/user/{MODRINTH_ID}/projects"
    headers = {"User-Agent": "GitHub-Actions-Modrinth-Discord-Bot (contact@yourdomain.com)"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json()
        
        # Filter for resource packs only
        resource_packs = [p for p in projects if p.get("project_type") == "resource_pack"]
        
        if not resource_packs:
            print("No resource packs found on this profile.")
            return None
            
        # Sort by creation or modification date to get the newest one
        resource_packs.sort(key=lambda x: x['updated'], reverse=True)
        return resource_packs[0]
        
    except Exception as e:
        print(f"Error fetching data from Modrinth: {e}")
        sys.exit(1)

def main():
    latest_pack = get_latest_resource_pack()
    if not latest_pack:
        return

    project_id = latest_pack['id']
    title = latest_pack['title']
    slug = latest_pack['slug']
    description = latest_pack.get('description', '')
    icon_url = latest_pack.get('icon_url', '')
    project_url = f"https://modrinth.com/resourcepack/{slug}"

    # Read the last processed project ID
    last_id = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = f.read().strip()

    # If it's a new project, send to Discord
    if project_id != last_id:
        print(f"New resource pack detected: {title}. Sending to Discord...")
        
        # Format a nice Discord embed message
        payload = {
            "embeds": [{
                "title": f"🆕 New Resource Pack: {title}",
                "description": description,
                "url": project_url,
                "color": 16747008,  # Orange/Modrinth theme color
                "thumbnail": {"url": icon_url} if icon_url else None,
                "footer": {"text": "Modrinth Update Alerter"}
            }]
        }
        
        discord_response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if discord_response.status_code in [200, 204]:
            print("Successfully sent to Discord.")
            # Update the state file with the new ID
            with open(STATE_FILE, "w") as f:
                f.write(project_id)
        else:
            print(f"Failed to send to Discord: {discord_response.status_code}")
            sys.exit(1)
    else:
        print("No new resource pack detected since last run.")

if __name__ == "__main__":
    main()
