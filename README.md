#### In development

# C practice SSH honey pot project

## Requirements
* cmake to build
* docker to run app
* create a SSH server
* logs all actions of user
* should allow the following commands
    * cat
    * wget
    * ps
    * whoami
    * ls
* MOTD should be configurable
* "user" and "password" should be configurable


## Bonus points
* Fake directory structure to then allow below commands
    * cd
    * ls (better version than above)
* Configuration file to vary honey pot



# To build libssh
Requires cmake and a C compiler
```
git submodule init
git submodule update
cd libssh
mkdir build
cd build
cmake ../.
make
sudo make install
```
