Add Micromamba support to PyCharm.

#### How to use

1. Clone this repo.
2. (Only for Windows User)
   Create file `conda.bat` in the clone repo, The content of the file is roughly as follows

   ```bash
   @echo off
   set MAMBA_ROOT_PREFIX=xxx
   set PATH=%PATH%;yyy
   set MAMBA_EXE=zzz
   python "C:\Users\pk5ls\micromamba-pycharm\conda" %*
   ```

   - Set `MAMBA_ROOT_PREFIX` environment variable for micromamba (see [Micromamba Installation — documentation](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html#windows) for more information about `MAMBA_ROOT_PREFIX`).
   - Add the folder containing the micromamba executable (i.e., the location of  `micromamba.exe `) to the end of the `%PATH%`environment variable.
   - Set `MAMBA_EXE` environment variable for micromamba executable file.
3. Use `./conda self-check` to see if your shell environment is set up correctly.
4. Configure PyCharm: In the *Add Python Interpreter* dialog, select *Conda Environment* and set *Conda executable* to the full path of the `conda` file (On Windows, conda.bat) of the cloned repo.

#### Debugging

Logs are written to `~/.cache/micromamba-pycharm.log`.
You can use them to debug problems.
Please attach the logs when filing a bug report.
