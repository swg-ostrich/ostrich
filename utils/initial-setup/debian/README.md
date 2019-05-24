## Debian Initial Setup
 1. Install Debian 9 x64-bit (I used `debian-9.4.0-amd64-netinst.iso`)
 2. As `root`, run `apt update; apt install sudo git`
 3. Run `git clone --recurse-submodules -j8 git://github.com/swg-ostrich/ostrich.git; cd ostrich`
 4. Run `./utils/initial-setup/debian/setup.sh`, reboot when it tells you to
     * user running the script must have privileges to use `sudo`
 5. Environment should be completely setup at this point
