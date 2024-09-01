
# 📆 RAK menus to iCal

> This project is not affiliated with the RAK or IMT Atlantique school. It's just a personal project to improve student's life on campus. The data is publicly provided by the RAK restaurant on their website.

This project was designed to import menus from the restaurant [RAK Plouzané](http://services.imt-atlantique.fr/rak/) into its iOS calendar. It is therefore mainly intended for IMT Atlantique Brest students.

The calendar is refreshed every Monday at 8 AM.


## Import the calendar

To use the ICS calendar and get the menus in your calendar (on your iPhone for example) :

**1st method - Easiest way (recommanded) :**
Just click on the next button, it will redirect you to the iCal URL and automatically open the calendar in your app :<br /><br />
![Static Badge](https://img.shields.io/badge/Click_to_import-g?style=flat&logo=Google%20Calendar&logoColor=white&label=ICS%20Calendar&link=http%3A%2F%2Fjordanbmrd.github.io%2Fical-rak-menu%2Fmenus.ics)

**2nd method - Add a new Mail account :**
1. Go to `Settings > Mail > Accounts`.
2. Add an account by selecting `Other` and `Add Subscrived Calendar`.
3. Add the ICS Calendar URL : `https://jordanbmrd.github.io/ical-rak-menu/` and leave other default parameters.

This configuration will allow the calendar to refresh by itself.
It should be almost the same configuration for Android or other OS.

Enjoy !

## Run it locally

1. Clone the repository
2. Install the dependencies :
```bash
pip install lxml ics requests
```

3. Run the script :
```bash
python create_calendar.py
```

This will create a new `menus.ics` file that you can import in any calendar app that supports ICS files.
