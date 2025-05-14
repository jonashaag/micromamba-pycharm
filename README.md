Add Micromamba support to PyCharm.

#### Looking for maintainers

I've stopped using Micromamba because I switched to [Pixi](https://pixi.sh/).

This project is currently not actively maintained.

If you are interested in helping with development of this project, please let me know.

#### How to use

1. Clone this repo.
2. Use `./conda self-check` to see if your shell environment is set up correctly.
3. Configure PyCharm: In the *Add Python Interpreter* dialog, select *Conda Environment* and set *Conda executable* to the full path of the `conda` file of the cloned repo.

#### Debugging

Logs are written to `~/.cache/micromamba-pycharm.log`.
You can use them to debug problems.
Please attach the logs when filing a bug report.
