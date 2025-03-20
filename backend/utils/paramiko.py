import re
import time
from paramiko import SSHClient, AutoAddPolicy, SSHException

class Paramiko:
    def __init__(self, hostname, username, password):
        """
        Initialize the Paramiko class
        :param hostname: The hostname of the remote host
        :param username: The username to use
        :param password: The password to use
        """
        self.hostname = hostname
        self.username = username
        self.password = password

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self._connect()
        self.channel = self.ssh.invoke_shell()

    def _connect(self):
        """
        Connect to the remote host
        """
        try:
            self.ssh.connect(
                hostname=self.hostname, username=self.username, password=self.password
            )

        except SSHException as e:
            raise RuntimeError(f"Failed to connect to {self.hostname}: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}")

    def execute(self, command):
        """
        Execute a command on the remote host
        :param command: The command to execute
        :return: A tuple containing the stdout and stderr
        """
        stdin, stdout, stderr = self.ssh.exec_command(command)
        
        return stdout.read().decode(), stderr.read().decode()
    
    def invoke(self, command, expected_output, timeout=10):
        """
        Workaround way of executing a command on custom CLI
        :param command: The command to execute
        :param expected_output: The expected output to wait before ending
        :param timeout: The timeout to wait for the expected output
        :return: String of the output 
        """        
        output = ""
        start_time = time.time()

        self.channel.send(command + "\n")

        is_stdout = False

        while True:
            if self.channel.recv_ready():
                curr_output = self.channel.recv(4096).decode('utf-8')
                if is_stdout:
                    output += curr_output
                if ">" in curr_output:
                    is_stdout = True
                if re.search(expected_output, curr_output):
                    break
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout occurred while executing `{command}`")

        return output

    def close(self):
        """
        Close the connection to the remote host
        """
        self.ssh.close()

