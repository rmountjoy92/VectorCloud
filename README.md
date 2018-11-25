![alt text](https://i.imgur.com/PadNQgV.png)
# VectorCloud
My goal with this project is to create a web interface using Flask for controlling vector, displaying information, and organizing (and possibly scheduling) sdk programs to run. My inspiration for this project comes from https://octoprint.org/ which is a web interface for controlling my 3d printer.

Here is a list of features I want to include in this project, if you have anything to add to list let me know and I will put it on here. I will be constantly adding things as I learn more about the SDK.

Disclaimer - I am a busy person and will be working on this in my free time. Please feel free to
contribute.

## How to run
* create a virtual environment https://packaging.python.org/guides/installing-using-pip-and-virtualenv/
* put the SDK folder into the virtual environment directory
* install as per the directions in the docs folder of the SDK folder
* in a terminal, navigate to your sdk folder. From inside your SDK folder enter:
```
git clone https://github.com/rmountjoy92/VectorCloud
pip3 install flask flask-sqlalchemy flask-bcrypt flask-login flask-wtf flask-bootstrap
```
* navigate to the VectorCloud folder, make sure run.py is executable and enter:
```
./run.py
```
* Open a browser and go to http://localhost:5000
* to stop the server press ctrl+c in the terminal


## Current Features
* view battery information provided by vector
* display battery voltage level as icon on navbar
* view cube information provided by vector
* added a button for vector to go pick up his cube (unreliable; will get better with next SDK release)
* dock/undock vector from buttons on navbar
* display version number provided by vector on navbar
* stage mulitple robots commands via interactive form and bulk send commands to vector
* SQLite database for storing commands, output, applications and users
* user authentication and registration, all routes are blocked unless user logs in
* upload python scripts to server, save as application with name, description and picture, support files
* edit and delete sdk apps

## Soon
* use try except blocks for running on Windows
* develop RESTFUL API
* add network state, pose, status output to status
* add more buttons to home screen for more robot functions
* animations list page with links with ability to click to animate vector (all thousands of them) with search option.
* create a text box to type in text to display on vector's face



## Eventually
* set up uWSGI
* create a 'control' page that contains the remote control SDK example
* plugin manager
* manage photos and videos
* interaction with cube lights
* learn the 'events' module and integrate it in some way
