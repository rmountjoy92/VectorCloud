# VectorCloud
![alt text](https://i.imgur.com/yQ6QaWD.png)
![alt text](https://i.imgur.com/AMQkLEW.png)
![alt text](https://i.imgur.com/wMgj8X9.png)

My goal with this project is to create a web interface using Flask for controlling vector, displaying information, and organizing (and possibly scheduling) sdk programs to run. My inspiration for this project comes from https://octoprint.org/ which is a web interface for controlling my 3d printer.

Please feel free to contribute.

## How to run
* make sure git is installed on your machine
* (recommended) create a virtual environment https://www.pythonforbeginners.com/basics/how-to-use-python-virtualenv/
* (recommended) navigate to your virtual environment.
* Install the SDK as per the directions in the SDK docs https://developer.anki.com/vector/docs/initial.html
* In a terminal, enter:
```
git clone https://github.com/rmountjoy92/VectorCloud
pip3 install flask flask-sqlalchemy flask-bcrypt flask-login flask-wtf flask-bootstrap flask-migrate flask-script
```
* navigate to the VectorCloud folder, make sure run.py is executable and enter:
On Linux or Mac:
```
./run.py 
```
On Windows:
```
py run.py
```

* Open a browser and go to http://localhost:5000
* to stop the server press ctrl+c in the terminal

## Notes
* do not update vectorcloud with git pull, use the built-in update system, as it makes the necessary changes to the database file.

## Current Features
* view information exposed by Vector on a webpage - battery level, ip, name, and much more!
* Install and manage applications for Vector by installing a VectorCloud package or uploading a script
* Install sample applications from an App Store
* export installed applications as packages
* Remote control Vector from the interface
* Stage and send SDK commands from a form on the home page
* Create, edit and delete a user login
* Customizable login message


## Features I'm currently working on
* create more store apps
* fix bugs
* develop RESTFUL API
* add network state and pose to status


## Features I plan to do in the future
* set up uWSGI, or some other production server
* create a Raspberry Pi image - once someone figures out how to run the sdk on it.
* plugin manager
* manage photos and videos
* learn the 'events' module and integrate it in some way

