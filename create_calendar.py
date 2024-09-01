import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
from ics import Calendar, Event
import pytz


def get_menu_by_date_and_time(rss_url, target_date, meal_time):
    """
    Cette fonction récupère le menu d'un flux RSS en fonction de la date et du moment du repas (midi ou soir).

    Parameters:
    rss_url (str): URL du flux RSS contenant les menus
    target_date (str): Date du menu souhaité au format 'dd/mm/yyyy'
    meal_time (str): Moment du repas ('midi' ou 'soir')

    Returns:
    str: Le menu pour la date et le moment spécifiés
    """
    # Téléchargement du flux RSS
    response = requests.get(rss_url)
    response.raise_for_status()  # Vérifie que la requête a réussi

    # Parsing du contenu XML
    root = ET.fromstring(response.content)

    # Conversion de la date cible au format datetime
    target_date_dt = datetime.strptime(target_date, "%d/%m/%Y")
    target_day_name = target_date_dt.strftime("%A").capitalize()  # Ex: 'Lundi', 'Mardi', etc.

    # Dictionnaire pour traduire les noms de jours en français
    days_translation = {
        "Monday": "Lundi",
        "Tuesday": "Mardi",
        "Wednesday": "Mercredi",
        "Thursday": "Jeudi",
        "Friday": "Vendredi",
        "Saturday": "Samedi",
        "Sunday": "Dimanche"
    }

    target_day_name_fr = days_translation.get(target_day_name, target_day_name)

    # Rechercher le bon élément <item> pour la semaine concernée
    for item in root.findall(".//item"):
        description = item.find("description").text

        # Nettoyage du contenu CDATA
        description = re.sub(r'<!\[CDATA\[|\]\]>', '', description)
        description = re.sub(r'<[^>]+>', '', description).replace("&nbsp;", " ").strip()

        # Séparation des jours
        days_sections = re.split(r'---\s*(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s*---', description)

        if target_day_name_fr in days_sections:
            index = days_sections.index(target_day_name_fr)
            day_menu_section = days_sections[index + 1]

            if meal_time.lower() == 'midi':
                meal_section = re.search(r"\| Dejeuner \|(.+?)(\| Diner \||$)", day_menu_section, re.S)
            else:
                meal_section = re.search(r"\| Diner \|(.+?)(\|---|$)", day_menu_section, re.S)

            if meal_section:
                menu = meal_section.group(1).strip()
                menu = menu.replace("|", "\n").strip()

                # Suppression des lignes contenant "***Rampe***" et ajout de tirets
                menu_lines = menu.splitlines()
                menu_cleaned = "\n".join(
                    f"- {line.strip()}" for line in menu_lines if "***Rampe***" not in line and line.strip()
                )

                return menu_cleaned

    return f"Aucun menu trouvé pour {target_day_name_fr} au {meal_time}."


def create_calendar_with_menus(rss_url, output_file):
    """
    Cette fonction crée un calendrier ICS avec les menus du midi et du soir pour chaque jour à partir d'aujourd'hui jusqu'au dernier jour disponible dans le flux RSS.

    Parameters:
    rss_url (str): URL du flux RSS contenant les menus
    output_file (str): Nom du fichier ICS de sortie
    """
    calendar = Calendar()

    # Définir le fuseau horaire français
    tz = pytz.timezone("Europe/Paris")

    # Téléchargement du flux RSS
    response = requests.get(rss_url)
    response.raise_for_status()  # Vérifie que la requête a réussi

    # Parsing du contenu XML
    root = ET.fromstring(response.content)

    # Obtenir la date actuelle
    current_date = datetime.now()

    # Boucle sur chaque <item> pour récupérer les menus
    for item in root.findall(".//item"):
        title = item.find("title").text
        date_range_match = re.search(r'du (\d{2}/\d{2}/\d{4}) au (\d{2}/\d{2}/\d{4})', title)
        if date_range_match:
            start_date_str = date_range_match.group(1)
            end_date_str = date_range_match.group(2)

            start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

            # Si la date de début est postérieure à la date actuelle, on continue à traiter ce menu
            if start_date >= current_date:
                day_date = start_date
                while day_date <= end_date:
                    # Ignorer les dimanches
                    if day_date.strftime("%A") == "Sunday":
                        day_date += timedelta(days=1)
                        continue

                    date_str = day_date.strftime("%d/%m/%Y")

                    print("\nOn : ", day_date)

                    # Récupérer le menu du midi
                    lunch_menu = get_menu_by_date_and_time(rss_url, date_str, "midi")
                    print("Déjeuner :\n", lunch_menu, sep="")
                    if lunch_menu and "fermé" not in lunch_menu.lower():
                        lunch_event = Event()
                        lunch_event.name = "Menu du midi"
                        lunch_event.begin = tz.localize(day_date.replace(hour=12, minute=15))
                        lunch_event.description = lunch_menu
                        lunch_event.duration = timedelta(hours=0.75)
                        calendar.events.add(lunch_event)

                    # Récupérer le menu du soir
                    dinner_menu = get_menu_by_date_and_time(rss_url, date_str, "soir")
                    print("Dîner :\n", dinner_menu, sep="")
                    if dinner_menu and "fermé" not in dinner_menu.lower():
                        dinner_event = Event()
                        dinner_event.name = "Menu du soir"
                        dinner_event.begin = tz.localize(day_date.replace(hour=19, minute=15))
                        dinner_event.description = dinner_menu
                        dinner_event.duration = timedelta(hours=0.75)
                        calendar.events.add(dinner_event)

                    # Passer au jour suivant
                    day_date += timedelta(days=1)

    # Sauvegarder le fichier ICS
    with open(output_file, 'w') as f:
        f.writelines(calendar)


# Exemple d'appel à la fonction
rss_url = "http://services.imt-atlantique.fr/rak/rss/menus.xml"
output_file = "menus.ics"
create_calendar_with_menus(rss_url, output_file)
