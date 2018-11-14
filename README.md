# VectorCloud
My goal with this project is to create a web interface using Flask for controlling vector, displaying information, and organizing (and possibly scheduling) sdk programs to run. My inspiration for this project comes from https://octoprint.org/ which is a web interface for controlling my 3d printer. 

Here is a list of features I want to include in this project, if you have anything to add to list let me know and I will put it on here. I will be constantly adding things as I learn more about the SDK.

Disclaimer - I am a busy person and will be working on this in my free time. Please feel free to
contribute.
## Current Features
* view battery information provided by vector
* display battery voltage level as icon on navbar
* view cube information provided by vector
* added a button for vector to go pick up his cube (unreliable; will get better with next SDK release)
* dock/undock vector from buttons on navbar
* display version number provided by vector on navbar
* stage mulitple robots commands via interactive form and bulk send commands to vector

## Soon
* create SQLAlchemy database for storing commands and remove all global variables
* develop RESTFUL API
* document code
* create how to install/run section in readme
* create a login function to prevent unauthorized access
* add network state, pose, status output to status
* add more buttons to home screen for more robot functions
* animations list page with links with ability to click to animate vector (all thousands of them) with search option.
* create a text box to type in text to display on vector's face


## Eventually
* set up uWSGI
* make pages load more dynamically
* create 'waiting on vector' animated .gif for load times
* create a way to easily store sdk applications to server and be able to run them with click of an icon.
* create a 'control' page that contains the remote control SDK example
* plugin manager
* manage photos and videos
* interaction with cube lights
* learn the 'events' module and integrate it in some way
