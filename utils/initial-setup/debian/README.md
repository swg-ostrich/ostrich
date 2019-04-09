## Debian Initial Setup
 1. Install Debian 9 x64-bit (I used `debian-9.4.0-amd64-netinst.iso`)
 2. Run `sudo apt-get update`
 3. Run `sudo apt-get install git`
 4. Run `git clone -b new-pipeline https://github.com/SWG-Source/swg-main.git; cd swg-main`
 5. Run `./utils/initial-setup/debian/setup.sh`, reboot when it tells you to
 8. Environment should be completely setup at this point
