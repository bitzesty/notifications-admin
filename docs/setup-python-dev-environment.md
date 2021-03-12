# Setting up your local Python environment

## Install Pyenv
### MacOS

MacOS ships with `python` and `python3` binaries, though these are somewhat out-of-date and will inevitably require root/sudo permissions to make changes. Our first step, therefore, is to use [`homebrew`](https://brew.sh/) to install `pyenv`, a command-line tool for installing and switching between different Python runtimes.

```
brew install pyenv
```

### Linux
```
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

Update your shell's config file (e.g. `~/.bashrc` for bash or `~/.zshrc` for zsh), adding `.pyenv/bin` to your $PATH variable:
```
PATH=$PATH:~/.pyenv/bin
```

### Windows
The [pyenv-win](https://github.com/pyenv-win) team have ported `pyenv` over to Microsoft Windows and, helpfully, offer multiple installation options. Check out [their documentation](https://github.com/pyenv-win/pyenv-win#installation) to find an installation option that works best for you.


## Initalize Pyenv whenever a new terminal session begins
Once you've installed `pyenv`, you'll need to add a single command to your shell's configuration file, initializing `pyenv` whenever a new shell window is started.
```
# For bash users:
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
source ~/.bashrc

# For ZSH users:
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.zshrc
source ~/.zshrc
```


## Configure Pyenv to use Python 3.6.x
Now that you have `pyenv` installed and set to initialize in each terminal session, let's use `pyenv` to install a particular version of python and set it as our global default.
You can search `pyenv` for the various version of Python 3.6 available for install. We recommend installing version 3.6.6

```
pyenv install --list | grep 3.6
pyenv install 3.6.6
pyenv global 3.6.6
```

## Install VirtualEnv
Once `pyenv` has finished installing your chosen version of Python, it's time to install a new tool, `virtualenv`, via Python's own package manager, `pip`.

```
pip install virtualenv
```
If you hadn't guessed from the name, `virtualenv` allows you to create a virtual python environment, relative to your codebase, that'll contain all of your installed python packages. Using `virtualenv` helps us to isolate our installed packages to the current project, without impacting other python projects that may be set up on our computer.
