# VectorCloud

* Discord Server - https://discord.gg/dtxBbwp

![alt text](https://i.imgur.com/EHWi6R3.png)
![alt text](https://i.imgur.com/AMQkLEW.png)
![alt text](https://i.imgur.com/JoB45zZ.png)
![alt text](https://i.imgur.com/NSWr7W6.png)

My goal with this project is to create a web interface using Flask for controlling vector, displaying information, and organizing (and possibly scheduling) sdk programs to run. My inspiration for this project comes from https://octoprint.org/ which is a web interface for controlling my 3d printer.

Please feel free to contribute.

## How to run
* make sure python>=3.6 is installed
* make sure git is installed on your machine
* (recommended) create a virtual environment https://www.pythonforbeginners.com/basics/how-to-use-python-virtualenv/
* (recommended) navigate to your virtual environment.
* In a terminal, enter:
```
git clone https://github.com/rmountjoy92/VectorCloud
cd VectorCloud
pip3 install -r requirements.txt
./run.py
```
* Note - on Windows you have to use:
```
py run.py
```

* Open a browser and go to http://localhost:5000
* to stop the server press ctrl+c in the terminal

## Notes
* Do not update vectorcloud with git pull, use the built-in update system, as it makes the necessary changes to the database file.

## Run in Docker

One-time installation:
```
docker-compose \
  -f docker-compose.yml \
  -f docker-compose-setup.yml \
  run --rm vectorcloud
```

Run VectorCloud:
```
docker-compose up vectorcloud
```

Open a browser and go to http://localhost:5000


## Current Features
* configure your Vector to use the SDK
* view information exposed by Vector on a webpage - battery level, ip, name, and much more!
* Install and manage applications for Vector by installing a VectorCloud package or uploading a script
* Install sample applications from an App Store
* export installed applications as packages
* Remote control Vector from the interface
* Stage and send SDK commands from a form on the home page
* Create, edit and delete a user login
* Customizable login message
* Update system that uses git to detect changes in the repository, updates using git pull and upgrades database using flask-migrate (alembic)
* REST API
* Interactive apps that communicate to the user through a prompt system

## How to contribute to the App Store
https://goo.gl/forms/OXI4jWu7hEDRAKd23

## Known Bugs
* That pesky white line on the battery and cube popovers.


## Features I'm currently working on
* create more store apps
* fix bugs
* add network state and pose to status


## Features I plan to do in the future
* create a Raspberry Pi image with production server
* plugin manager
* manage photos and videos
* learn the 'events' module and integrate it in some way
