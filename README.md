# 📆 RAK menus to iCal

This project was designed to import menus from the restaurant [RAK Plouzané](http://services.imt-atlantique.fr/rak/) into its iOS calendar. It is therefore mainly intended for IMT Atlantique Brest students.

The calendar is refreshed every Monday at 8 AM


## Import the calendar (iOS & others)

To use the ICS calendar and get the menus in your calendar (on your iPhone for example) :

1. Click on the `menus.ics` file
2. Click the `Raw` button

If you're on iOS, it should ask you to add the events in your calendar.
If you're on another platform, you should be able to open it in your favorite calendar app.

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
