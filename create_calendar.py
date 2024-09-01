import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
from ics import Calendar, Event
import pytz

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_menu_by_date_and_time(rss_url, target_date, meal_time):
    response = requests.get(rss_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    target_date_dt = datetime.strptime(target_date, "%d/%m/%Y")
    weekday_target = target_date_dt.strftime("%A").capitalize()  # en anglais

    # Traduction en français si nécessaire
    weekdays_fr = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
                   "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
                   "Sunday": "Dimanche"}
    weekday_target_fr = weekdays_fr[weekday_target]

    for item in root.findall(".//item"):
        title = item.find("title").text
        date_range = re.search(r'du (\d{2}/\d{2}/\d{4}) au (\d{2}/\d{2}/\d{4})', title)
        if date_range:
            start_week = datetime.strptime(date_range.group(1), "%d/%m/%Y")
            end_week = datetime.strptime(date_range.group(2), "%d/%m/%Y")

            if start_week <= target_date_dt <= end_week:
                description = item.find("description").text
                description = clean_html(description)  # Nettoyer le HTML

                # Recherche du jour spécifique
                day_pattern = rf"---\s*{weekday_target_fr}\s*---(.*?)---"
                day_menu_match = re.search(day_pattern, description, re.DOTALL)
                if day_menu_match:
                    day_menu = day_menu_match.group(1)


                    # Extraire la partie spécifique pour midi ou diner
                    if meal_time == "midi":
                        meal_section = day_menu.split("| Diner |")[0]
                        menu_items = meal_section.split("|")[2:-1]
                    else:
                        meal_section = day_menu.split("| Diner |")[1]
                        menu_items = meal_section.split("|")[0:-1]

                    # Nettoyer et formater les éléments du menu
                    print(menu_items)
                    menu_items = [f"{item.strip()}" for item in menu_items if item.strip()]
                    return menu_items

    return None


def create_calendar_with_menus(rss_url, output_file):
    calendar = Calendar()
    tz = pytz.timezone("Europe/Paris")

    response = requests.get(rss_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    for item in root.findall(".//item"):
        title = item.find("title").text
        date_range_match = re.search(r'du (\d{2}/\d{2}/\d{4}) au (\d{2}/\d{2}/\d{4})', title)
        if date_range_match:
            start_date_str = date_range_match.group(1)
            end_date_str = date_range_match.group(2)

            start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

            day_date = start_date
            while day_date <= end_date:
                if day_date.strftime("%A") != "Sunday":  # Ignorer les dimanches
                    date_str = day_date.strftime("%d/%m/%Y")
                    print("\nDate : ", date_str)

                    for meal_time in ["midi", "soir"]:
                        menu = get_menu_by_date_and_time(rss_url, date_str, meal_time)
                        if menu:
                            event = Event()
                            event.name = ", ".join(menu)
                            hour = 12 if meal_time == "midi" else 19
                            event.begin = tz.localize(day_date.replace(hour=hour, minute=15))
                            event.description = "\n".join(f"- {item}" for item in menu)
                            event.duration = timedelta(hours=0.75)
                            calendar.events.add(event)

                            print(f"{meal_time.capitalize()} :\n{menu}")

                day_date += timedelta(days=1)

    with open(output_file, 'w') as f:
        f.writelines(calendar)

# Exemple d'appel à la fonction
rss_url = "http://services.imt-atlantique.fr/rak/rss/menus.xml"
output_file = "menus.ics"
create_calendar_with_menus(rss_url, output_file)
