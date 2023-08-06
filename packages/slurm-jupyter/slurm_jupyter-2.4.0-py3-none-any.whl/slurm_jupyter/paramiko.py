
def async_ssh(cmd_dict):
    import paramiko
    from paramiko.buffered_pipe import PipeTimeout
    from paramiko.ssh_exception import (SSHException, PasswordRequiredException)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    retries = 0
    while True:  # Be robust to transient SSH failures.
        try:
            # Set paramiko logging to WARN or higher to squelch INFO messages.
            import logging
            logger = logging.getLogger('paramiko')
            logger.setLevel(logging.WARN)

            ssh.connect(hostname = cmd_dict['address'],
                        username = cmd_dict['ssh_username'],
                        port = cmd_dict['ssh_port'],
                        key_filename = cmd_dict['ssh_private_key'],
                        compress = True,
                        timeout = 20,
                        banner_timeout = 20)  # Helps prevent timeouts when many concurrent ssh connections are opened.


            # Connection successful, break out of while loop
            break

        except (SSHException,
                PasswordRequiredException) as e:

            print('[ dask-ssh ] : ' + bcolors.FAIL +
                  'SSH connection error when connecting to {addr}:{port} to run \'{cmd}\''.format(addr = cmd_dict['address'],
                                                                                                  port = cmd_dict['ssh_port'],
                                                                                                  cmd = cmd_dict['cmd']) +
                  bcolors.ENDC)
            print( bcolors.FAIL + '               SSH reported this exception: ' + str(e) + bcolors.ENDC )

            # Print an exception traceback
            traceback.print_exc()

            # Transient SSH errors can occur when many SSH connections are
            # simultaneously opened to the same server. This makes a few
            # attempts to retry.
            retries += 1
            if retries >= 3:
                print( '[ dask-ssh ] : ' + bcolors.FAIL + 'SSH connection failed after 3 retries. Exiting.' + bcolors.ENDC)

                # Connection failed after multiple attempts.  Terminate this thread.
                os._exit(1)

            # Wait a moment before retrying
            print( '               ' + bcolors.FAIL +
                   'Retrying... (attempt {n}/{total})'.format(n = retries, total = 3) +
                   bcolors.ENDC)

            sleep(1)


    # Execute the command, and grab file handles for stdout and stderr. Note
    # that we run the command using the user's default shell, but force it to
    # run in an interactive login shell, which hopefully ensures that all of the
    # user's normal environment variables (via the dot files) have been loaded
    # before the command is run. This should help to ensure that important
    # aspects of the environment like PATH and PYTHONPATH are configured.

    print('[ {label} ] : {cmd}'.format(label = cmd_dict['label'],
                                       cmd = cmd_dict['cmd']))
    stdin, stdout, stderr = ssh.exec_command('$SHELL -i -c \'' + cmd_dict['cmd'] + '\'', get_pty = True)

    # Set up channel timeouts (which we rely on below to make readline()
    # non-blocking.
    stdout.channel.settimeout(0.1)
    stderr.channel.settimeout(0.1)

    # Wait for a message on the input_queue. Any message received signals this
    # thread to shut itself down.
    while(cmd_dict['input_queue'].empty()):

        # Read stdout stream, time out if necessary.
        try:
            line = stdout.readline()
            while len(line) > 0:    # Loops until a timeout exception occurs
                cmd_dict['output_queue'].put('[ {label} ] : {output}'.format(label = cmd_dict['label'],
                                                                             output = line.rstrip()))
                line = stdout.readline()

        except PipeTimeout:
            continue
        except socket.timeout:
            continue

        # Read stderr stream, time out if necessary
        try:
            line = stderr.readline()
            while len(line) > 0:
                cmd_dict['output_queue'].put('[ {label} ] : '.format(label = cmd_dict['label']) +
                                             bcolors.FAIL + '{output}'.format(output = line.rstrip()) + bcolors.ENDC)
                line = stderr.readline()

        except PipeTimeout:
            continue
        except socket.timeout:
            continue

        # Check to see if the process has exited. If it has, we let this thread
        # terminate.
        if stdout.channel.exit_status_ready():
            exit_status = stdout.channel.recv_exit_status()
            cmd_dict['output_queue'].put('[ {label} ] : '.format(label = cmd_dict['label']) +
                                         bcolors.FAIL +
                                         "remote process exited with exit status " +
                                         str(exit_status) + bcolors.ENDC)
            break

        # Kill some time so that this thread does not hog the CPU.
        sleep(1.0)

    # end while()

    # Shutdown the channel, and close the SSH connection
    stdout.channel.close()
    stderr.channel.close()
    ssh.close()