import json
import os
import requests

# --- KONFIGURACJA ---
MODRINTH_USERNAME = "HypX2L"  # Wpisz tutaj swoją dokładną nazwę użytkownika z Modrinth
CACHE_FILE = "Discord/last_posted_project.txt"
USER_AGENT = "MyDiscordProfileBot/1.0 (contact@example.com)"
# ---------------------

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def check_profile_and_post():
    if not DISCORD_WEBHOOK_URL:
        print("Błąd: Zmienna DISCORD_WEBHOOK_URL nie istnieje w GitHub Secrets.")
        return

    headers = {"User-Agent": USER_AGENT}
    user_url = f"https://modrinth.com{MODRINTH_USERNAME}/projects"
    response = requests.get(user_url, headers=headers)

    if response.status_code != 200:
        print(f"Nie udało się pobrać profilu Modrinth. Kod błędu: {response.status_code}")
        return

    projects = response.json()
    if not projects:
        print("Nie znaleziono żadnych projektów na tym profilu.")
        return

    # Sortowanie, aby znaleźć najnowszy opublikowany paczkę tekstur
    projects.sort(key=lambda x: x.get("published", ""), reverse=True)
    newest_project = projects[0]
    
    project_id = newest_project["id"]
    project_slug = newest_project["slug"]
    title = newest_project["title"]
    description = newest_project.get("description", "")
    icon_url = newest_project.get("icon_url", "")

    # Sprawdzenie pamięci podręcznej (cache), aby uniknąć spamu
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            if f.read().strip() == project_id:
                print("Brak nowych projektów na profilu. Wszystko jest aktualne.")
                return

    # Przygotowanie wyglądu wiadomości Discord
    payload = {
        "embeds": [
            {
                "title": f"🆕 New Recource Pack: {title}",
                "url": f"https://modrinth.com{project_slug}",
                "description": f"**description:**\n{description[:1000]}",
                "color": 5814783,
                "thumbnail": {"url": icon_url} if icon_url else {},
                "footer": {"text": f" Sent By {MODRINTH_USERNAME}"},
            }
        ]
    }

    # Wysyłanie na Discord
    webhook_res = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    # Poprawiony warunek statusu kodu (200 lub 204 oznacza sukces)
    if webhook_res.status_code in [200, 204]:
        print(f"Sukces! Wysłano '{title}' na Discorda.")
        
        # Tworzenie folderu jeśli nie istnieje i zapis cache
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            f.write(project_id)
    else:
        print(f"Błąd wysyłania na Discord. Status: {webhook_res.status_code}")
        print(webhook_res.text)


if __name__ == "__main__":
    check_profile_and_post()
