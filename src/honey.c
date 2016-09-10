#include <stdio.h>

#include "libssh/libssh.h"
#include "libssh/server.h"


int main(int agrc, char **argv)
{
        ssh_bind sshbind;
        ssh_session session;

        sshbind = ssh_bind_new();
        session = ssh_new();

        if (ssh_bind_listen(sshbind) < 0) {
                printf("Error: %s\n", ssh_get_error(sshbind));
                return 1;
        }

        int r = ssh_bind_accept(sshbind, session);
        if (r == SSH_ERROR) {
                printf("Error: %s", ssh_get_error(sshbind));
        }

        return 0;
}
