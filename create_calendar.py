from ics import Calendar, Event
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re


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

    target_day_name_fr = days_translation[target_day_name]

    # Rechercher le bon élément <item> pour la semaine concernée
    for item in root.findall(".//item"):
        description = item.find("description").text

        # Vérifie si la date du jour correspond à celle du menu
        if target_day_name_fr in description:
            # Nettoyage du contenu CDATA
            description = re.sub(r'<!\[CDATA\[|\]\]>', '', description)
            description = re.sub(r'<[^>]+>', '', description).replace("&nbsp;", " ").strip()

            if meal_time.lower() == 'midi':
                start = description.find(f"| Dejeuner |")
                end = description.find("| Diner |")
            else:
                start = description.find(f"| Diner |")
                end = description.find("---", start)

            # Extrait le menu entre les balises correctes
            if start != -1 and end != -1:
                menu = description[start:end].replace("|", "\n").strip()

                # Suppression des lignes contenant "***Rampe***"
                menu_lines = menu.splitlines()
                menu_cleaned = "\n".join(line for line in menu_lines if "***Rampe***" not in line)

                return menu_cleaned

    return f"Aucun menu trouvé pour {target_day_name_fr} au {meal_time}."


def create_calendar_with_menus(rss_url, start_date, end_date, output_file):
    """
    Cette fonction crée un calendrier ICS avec les menus du midi et du soir pour chaque jour entre deux dates.

    Parameters:
    rss_url (str): URL du flux RSS contenant les menus
    start_date (str): Date de début au format 'dd/mm/yyyy'
    end_date (str): Date de fin au format 'dd/mm/yyyy'
    output_file (str): Nom du fichier ICS de sortie
    """
    calendar = Calendar()

    # Conversion des dates en objets datetime
    start_date_dt = datetime.strptime(start_date, "%d/%m/%Y")
    end_date_dt = datetime.strptime(end_date, "%d/%m/%Y")

    # Boucle sur chaque jour entre start_date et end_date
    current_date = start_date_dt
    while current_date <= end_date_dt:
        date_str = current_date.strftime("%d/%m/%Y")

        # Récupérer le menu du midi
        lunch_menu = get_menu_by_date_and_time(rss_url, date_str, "midi")
        if lunch_menu:
            lunch_event = Event()
            lunch_event.name = "Menu du midi"
            lunch_event.begin = current_date.replace(hour=12, minute=15)
            lunch_event.description = lunch_menu
            lunch_event.duration = timedelta(hours=0.75)
            calendar.events.add(lunch_event)

        # Récupérer le menu du soir
        dinner_menu = get_menu_by_date_and_time(rss_url, date_str, "soir")
        if dinner_menu:
            dinner_event = Event()
            dinner_event.name = "Menu du soir"
            dinner_event.begin = current_date.replace(hour=19, minute=15)
            dinner_event.description = dinner_menu
            dinner_event.duration = timedelta(hours=0.75)
            calendar.events.add(dinner_event)

        # Passer au jour suivant
        current_date += timedelta(days=1)

    # Sauvegarder le fichier ICS
    with open(output_file, 'w') as f:
        f.writelines(calendar)


# Exemple d'appel à la fonction
rss_url = "http://services.imt-atlantique.fr/rak/rss/menus.xml"
start_date = "16/09/2024"  # Date de début
end_date = "22/09/2024"  # Date de fin
output_file = "menus.ics"
create_calendar_with_menus(rss_url, start_date, end_date, output_file)
