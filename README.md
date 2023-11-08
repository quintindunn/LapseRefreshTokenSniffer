# LapseRefreshTokenSniffer

## How to use:

### Online (Simpler):
#### Start on your computer:
* Go to http://refreshtokens.lapsepy.quintindev.com/
* Click on `Generate Proxy`
* Not the credentials, these will be used later.

#### Onto your phone:
* Go to your camera app and scan the QR code, go to the link and copy the text.
* Go to settings > network > `<YOUR_NETWORK>` > i > proxy and select manual
* Enter the credentials, for the password you can just paste what you copied from the QR code.
* On safari go to `mitm.it` and follow the instructions for IOS.
* Go to the Lapse app and sign out.
* Sign back into Lapse.

#### Back onto your computer:
* The data should be shown in the box.

### Local (More complicated):
#### Start on your computer:
* Clone the repository `git clone https://github.com/quintindunn/LapseRefreshTokenSniffer.git`
* `cd` into the directory `cd LapseRefreshTokenSniffer`
* Create a virtual environment `python3 -m venv venv`
* Activate the virtual environment
* Install requirements `pip install -r requirements.txt`
* cd into the `webserver` folder `cd webserver`
* Run the `server.py` file
* Go to the URL in the console, and hit `Generate proxy` **stay on the page it redirects you to**
* Get your computer's IP address using `ipconfig`

#### Now onto your phone:
* Go to settings > network > `<YOUR_NETWORK>` > i > proxy and select manual
* Enter the credentials **Use the ip from `ipconfig`**
* Go to the url `mitm.it` on safari
* Follow the instructions for IOS
* Go to lapse, sign out, and sign back in.

## Back to your computer:
* Look in the box and your credentials should be there, for [LapsePy](https://github.com/quintindunn/lapsepy/) you'll want the `refresh-token`.
