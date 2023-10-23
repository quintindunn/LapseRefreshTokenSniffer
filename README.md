# LapseRefreshTokenSniffer

## How to use:

### Start on your computer:
* Clone the repository `git clone https://github.com/quintindunn/LapseRefreshTokenSniffer.git`
* `cd` into the directory `cd LapseRefreshTokenSniffer`
* Start the proxy server by running `run.bat`
* Get computer IPV4:
  * Open command prompt
  * Type `ipconfig`
  * Next to `IPv4 Address` will be your IP, it will look something like `192.168.1.10`

### Now onto your phone:
* Log out of Lapse
* Reopen Lapse
* Enter your phone number and hit next, wait for your verification code **DO NOT ENTER IT YET.**
* Go to `settings -> network -> <your wifi network> -> i -> Configure Proxy`
* Select manual
* Enter your computer IP in the `server` field
* Enter `8003` in the `port` field.
* Go back to Lapse and enter your verification code.
* Watch the output of the proxy for your codes.