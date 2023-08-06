import time
from pathlib import Path
import os
import warnings
import subprocess


class Datamover:
    """
    Python wrapper for the zih datamover tools that enable exchanging files between a project space on the cluster and a fileserver share via an export node.

    See also
    --------
    .. [0] https://doc.zih.tu-dresden.de/data_transfer/datamover/
    """

    def __init__(
            self, path_to_exe: str = '/sw/taurus/tools/slurmtools/default/bin/', blocking: bool = True, verbosity: int = 0):
        """
        Sets up a project-space - fileserver-mount connection.

        Parameters
        ----------
        path_to_exe : str
            Path to the datamover executables on the cluster, default: /sw/taurus/tools/slurmtools/default/bin/
        blocking : bool
            if set to True (default) the slurm jobs are spawned by srun, which runs in the foreground and we can see the output
            if set to False , the slurm jobs (except dtls) are spawned by sbatch, which runs the job in the background and we would need to extract the output from its log file
            Do not change this unless you have a good reason to do so.
        verbosity : int
            set the verbosity level.
            0 (default) : verbosity - all output is captured by subprocess and not printed. Both stdout and stderr can later be extracted from proc by `proc.communicate()` (which waits for the process to finish).
            1 : some verbosity - only stout is captured by subprocess and can be processed later. Errors are printed immediately (useful if you  want to know what is going on when you use Datamover directly in a jupyter notebook).
            2 : very verbose: all output is printed immediately and nothing is captured by subprocess
        """
        self.path_to_exe = Path(path_to_exe)
        self.blocking = blocking
        self.verbosity = verbosity
        dtfiles = self.path_to_exe.glob('dt*')
        self.exe = [f.name for f in dtfiles if os.access(f, os.X_OK)]
        if 'dtls' in self.exe:
            self.current_command = 'dtls'
        elif len(self.exe) > 0:
            self.current_command = self.exe[0]
        else:
            self.current_command = None

    def __getattr__(self, attr):
        '''
        Modify the __getattr__ special function: Each executable name in self.exe becomes a callable function that executes the respective shell script.
        '''
        if attr in self.exe:
            self.current_command = attr
            return self._execute
        else:
            raise AttributeError(attr)

    def _execute(self, *args):
        """
        Execute the current command with arguments and return its output.

        Parameters
        ----------
        args : list of str
            The arguments to the command to be executed, e.g. for the command "dtls" sensible arguments would be ["-l", "/foo/bar"]

        Returns
        -------
        subprocess.Popen object (see: https://docs.python.org/3/library/subprocess.html#popen-constructor)
        """
        # we append the argument "--blocking" so that datamover uses srun
        # instead of sbatch for all arguments. That way, we can use
        # subprocess.poll to figure out whether the operation has finished.
        # Also, dtls behaves the same as all other processes (by default all
        # processes except dtls use sbatch)
        args = [self.path_to_exe / self.current_command] + list(args)
        if self.blocking:
            args += ['--blocking']
        stdout = subprocess.PIPE if self.verbosity < 2 else None
        stderr = subprocess.PIPE if self.verbosity < 1 else None
        proc = subprocess.Popen(args, stdout=stdout, stderr=stderr)
        return proc

    def is_cluster(self):
        return len(self.exe) > 0


def waitfor(proc, timeout_in_s: float = -1,
            discard_output: bool = True) -> int:
    """
    Wait for a process to complete.

    Parameters
    ----------
    proc: subprocess.Popen object (e.g. returned by the Datamover class)
    timeout_in_s: float, optional (default: endless)
        Timeout in seconds. This process will be interrupted when the timeout is reached.
    discard_output: bool, optional (default: True)
        The default behavior is to discard dthe process output (to avoid leaving open file pointers). If you need the output of the command, use discard_output=True.
    Returns
    -------
    int exit code of the process
    """
    start_time = time.time()
    print("Waiting .", end='', flush=True)
    while proc.poll() is None:
        time.sleep(0.5)
        print(".", end='', flush=True)
        if timeout_in_s > 0 and (time.time() - start_time) > timeout_in_s:
            print("\n")
            warnings.warn(
                'Timeout while waiting for process: ' + ' '.join([str(arg) for arg in proc.args]))
            proc.kill()
            return proc.poll()
    exit_code = proc.poll()
    if discard_output:
        out, err = proc.communicate()
    if exit_code > 0:
        warnings.warn(
            'process: {}\nexited with error: {}\nand output: {}'.format(' '.join([str(arg) for arg in proc.args]), err, out))
    return proc.poll()
