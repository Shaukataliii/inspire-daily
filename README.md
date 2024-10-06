# How to set up?
Just run the set-as-startup-app.py and it will automatically set the main.py as start up application & that's it.

Now the app will start doing it work.
- Whenever you will turn ON the PC, it will display the quote and a Hadith notification (once/day).
- The app will check if the notification is displayed today or not after the setup duration i.e. 4 hours. So if you're on laptop and you don't turn it OFF, you're still at ease. You'll get a notification every day.
- Make sure to update the path of this system in the main.bat file before running set-as-start-up-app.py

## Features to add
- Development as a pypi


## Features
- Downloads the quotes dataset from kaggle and prepares it.
- Displays a quote daily when the system is turned on. After that, runs after specified number of hours to recheck the condition.
- Displays a hadith of the Prophet (PBUH) along with the quote.
- User can add a custom quote at any time.
