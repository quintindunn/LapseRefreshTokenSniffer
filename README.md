# LapseRefreshTokenSniffer

## How to use:

### Start on your computer:
* Clone the repository `git clone https://github.com/quintindunn/LapseRefreshTokenSniffer.git`
* `cd` into the directory `cd LapseRefreshTokenSniffer`
* Create a virtual environment `python3 -m venv venv`
* Activate the virtual environment
* Install requirements `pip install -r requirements.txt`
* cd into the `webserver` folder `cd webserver`
* Run the `server.py` file
* Go to the URL in the console, and hit `Generate proxy` **stay on the page it redirects you to**
* Get your computer's IP address using `ipconfig`
  
### Now onto your phone:
* Go to settings > network > `<YOUR_NETWORK>` > i > proxy and select manual
* Enter the credentials **Use the ip from `ipconfig`**
* Go to the url `mitm.it` on safari
* Follow the instructions for IOS
* Go to lapse, sign out, and sign back in.

## Back to your computer:
* Look in the box and your credentials should be there, for [LapsePy](https://github.com/quintindunn/lapsepy/) you'll want the `refresh-token`.
