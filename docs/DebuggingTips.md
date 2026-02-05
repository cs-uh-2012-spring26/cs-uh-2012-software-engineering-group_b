# Debugging Tips

## Getting the makefile to run

First, note that you are welcome to change how you run things as long as (1) you update the instructions in the README and (2) your instructions can be reproduced on different environments.

### I'm getting a python not found error

The current makefile assumes that the command `python` on your machine invokes `python3.10` or higher. We changed the makefile to check if `python` exists (not as an alias) and if not, use `python3` instead. Once inside the virtual environment, the command `python` works anyways.

If you are getting a python not found error, check which python version is installed on your machine and which of the above python commands exist. Line 19 in the makefile is where the python virtual environment is created. You can change this if needed, but make sure you don't break your team mate's setup. In general, whenever you make changes to the makefile (or however you run your project), make sure that the instructions work on all your team's machines.

## I'm running on windows and the makefile doesn't work

Turns out that the path to the venv on windows is different than on Linux-based platforms. We changed the makefile to account for that, but if it doesn't work for your Windows platform for any reason, check the makefile lines 4-9 and 22-26. These lines check for the keywords indicating a windows platform and adjust the venv path accordingly. If it's not working on your windows platform, you can check the version of windows you are running and what it's returned name is.

Feel free to further debug based on the error messages you receive. 

## I'm getting a different python error

- `ERROR: Could not find a version that satisfies the requirement flask==3.1.0` --> Are you sure you have python 3.10 or higher installed?

- `Error: Command '['/local/HDD1/home/sarah/Temp/flask-template/.venv/bin/python3', '-m', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1` --> it may be the case that for some reason you don't have the venv corresponding to your specific python version installed. See [https://stackoverflow.com/questions/69594088/error-when-creating-venv-error-command-im-ensurepip-upgrade-def](https://stackoverflow.com/questions/69594088/error-when-creating-venv-error-command-im-ensurepip-upgrade-def)

In general, debugging and solving errors is a core skill you want to gain. Don't shy away from searching for the error messages, trying different things, or even coming up with workarounds to move forward. For example, if the makefile isn't working for you and you need to finish your contributions, you can always run and test things "manually" by running the commands needed to create your venv, activate it, run pytest etc. Run locally like that until you solve any issues you have and your setup CI should hopefully be able to run things for your whole team to see.