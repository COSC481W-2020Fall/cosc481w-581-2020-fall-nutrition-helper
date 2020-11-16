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
### Local
1. Make sure you are inside the directory 'project'
2. Run `python manage.py runserver`
3. You should see the line `Starting development server at http://127.0.0.1:8000/`
4. Enter the address followed by nutrihacker into your browser: http://127.0.0.1:8000/nutrihacker/

### AWS for Teammates
1. Connect to the EC2 instance
2. Run `screen -r runserver` to reattach the screen the Django server is running on
3. You should automatically be in the 481/project directory and django-env virtual environment
    * The prompt should look like this: `(django-env) [ec2-user@ip project]`
4. Press Ctrl-C to stop the server
5. To start the server again, run `python manage.py runserver 0.0.0.0:8000`
6. To keep the server running in the background, detach the screen by pressing Ctrl-A, then Ctrl-D
7. Site address: http://3.88.6.165:8000/nutrihacker/

### Your Own AWS Server
1. Install Python packages from requirements.txt
2. Install latest version of SQLite
    1. Rename existing sqlite3 file in `/usr/bin` to something else, such as sqlite3.7
    2. [Download source code from SQLite website](https://www.sqlite.org/download.html)
    3. [Compile and install the binaries](https://sqlite.org/src/doc/trunk/README.md)
    4. [Tell Python to use the new version of SQLite](https://stackoverflow.com/a/55775310)
    5. Verify that your system is also using the latest version: `sqlite3 --version`
3. Add the public ip of your server to ALLOWED_HOSTS in nutrihelper/nutrihelper/settings.py 
4. Activate the virtual environment if you are using one
5. Run `python manage.py runserver 0.0.0.0:8000`
    * You may get the message `Error: That port is already in use.` In this case, run `sudo fuser -k 8000/tcp` to kill any processses on that port.
6. Address will be the public ip followed by :8000/nutrihacker: `http://[PUBLIC_IP]:8000/nutrihacker`
7. If the website doesn't load, it's probably due to the security group for your EC2 instance. Add a rule on Inbound for Custom TCP on port 8000.

## Members
* Bryce VanAsselt
* Michael Neet
* John Owens
* Athena Xia
* Jalen Hudson
* Tsion Tadesse
