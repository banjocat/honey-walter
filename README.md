#### In development

# C practice SSH honey pot project

Like all my practice projects I setup goals that I try to reach.

## Goals
* ~~cmake to build~~
* ~~docker to run app~~
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


## Bonus goals
* Fake directory structure to then allow below commands
    * cd
    * ls (better version than above)
* Configuration file to vary honey pot


# To build honeywalter
Requires openssl, cmake, libssh-dev and a C compiler
```
cmake .
make
```

`honeywalter` will be located in `./bin`


# Dockerfile
While there is a dockerfile it is intended more for deployment than development.
Developing with C in a Dockerfile is not ideal as it will always rebuild from scratch.
Perhaps there is a way around this.. if so please tell me :D

To run using docker use the expected `docker-compose up`
