
import paramiko
from paramiko.buffered_pipe import PipeTimeout
from paramiko.ssh_exception import (SSHException, PasswordRequiredException)

def ssh_command(cmd, spec):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    retries = 0
    while True:  # Be robust to transient SSH failures.
        try:
            # Set paramiko logging to WARN or higher to squelch INFO messages.
            import logging
            logger = logging.getLogger('paramiko')
            logger.setLevel(logging.WARN)
            ssh.connect(hostname = 'login.genome.au.dk,
                        username = 'kmt',
                        port = '22',
#                        key_filename = spec['ssh_private_key'],
                        compress = True,
                        timeout = 20,
                        banner_timeout = 20)  # Helps prevent timeouts when many concurrent ssh connections are opened.
            break

        except SSHException, PasswordRequiredException as e:
            traceback.print_exc()
            retries += 1
            if retries >= 3:
                os._exit(1)
            sleep(1)

    stdin, stdout, stderr = ssh.exec_command('$SHELL -i -c \'' + cmd + '\'', get_pty = True)

    # Set up channel timeouts (which we rely on below to make readline()
    # non-blocking.
    stdout.channel.settimeout(0.1)
    stderr.channel.settimeout(0.1)

    return ssh, stdout, stderr



ssh, stdout, stderr = ssh_command(cmd, spec)

while True:

    try:
        # Read stdout stream, time out if necessary.
        try:
            line = stdout.readline()
            while len(line) > 0:    # Loops until a timeout exception occurs
                line = stdout.readline()
        except PipeTimeout:
            continue
        except socket.timeout:
            continue
    except KeyboardInterrupt:
        break

stdout.channel.close()
stderr.channel.close()
ssh.close()
