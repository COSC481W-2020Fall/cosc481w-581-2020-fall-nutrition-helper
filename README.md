# Nutrition Helper

## Project
A website that helps with meal planning and provides nutrition information.

## Prototype Description
A simple webpage that can access the USDA nutrition facts database through two buttons: "Egg" and "Broccoli". The buttons will be basic buttons with text on them. Clicking on either button will retrieve the information (serving size, calories, total fat, cholesterol, sodium, total carb, protein) of that food and display it on the screen in a table. This page will be dynamically populated with that food's data that we will store on the server. The website will have a back button for users to return to the previous page to select a different meal if they would like to.

A use case diagram for this prototype may be found at https://app.lucidchart.com/publicSegments/view/069e1c84-fd26-4b98-ae55-51c4ec09040b/image.pdf

## Technologies
Project is created with:
* Python
* Django
* SQLite

## USDA Database
We are getting all of our nutrition information from the USDA database found here: https://fdc.nal.usda.gov/

## Running the Web Server
1. Make sure you are inside the directory 'project'
2. Run `python manage.py migrate`
3. Run `python manage.py runserver`
4. You should see the line `Starting development server at http://127.0.0.1:8000/`. The exact address may vary.
5. Enter the address followed by nutrihacker into your browser: `http://127.0.0.1:8000/nutrihacker/`.

### Running the Web Server on AWS
1. Add the public ip to ALLOWED_HOSTS in nutrihelper/nutrihelper/settings.py 
2. Run `python manage.py runserver 0.0.0.0:8000`
    * You may get the message `Error: That port is already in use.` In this case, run `sudo fuser -k 8000/tcp` to kill any processses on that port.
3. Enter the public ip followed by :8000/nutrihacker into your browser: `http://[PUBLIC_IP]:8000/nutrihacker`

## Members
* Bryce VanAsselt
* Michael Neet
* John Owens
* Athena Xia
* Jalen Hudson
* Tsion Tadesse
