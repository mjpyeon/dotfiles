#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('''
   @wookayin's              ███████╗██╗██╗     ███████╗███████╗
   ██████╗  █████╗ ████████╗██╔════╝██║██║     ██╔════╝██╔════╝
   ██╔══██╗██╔══██╗╚══██╔══╝█████╗  ██║██║     █████╗  ███████╗
   ██║  ██║██║  ██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
   ██████╔╝╚█████╔╝   ██║   ██║     ██║███████╗███████╗███████║
   ╚═════╝  ╚═════╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝

   https://dotfiles.wook.kr/
''')

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-f', '--force', action="store_true", default=False,
                    help='If specified, it will override existing symbolic links')
parser.add_argument('--vim-plug', default='update', choices=['update', 'install', 'none'],
                    help='vim plugins: update and install (default), install only, or do nothing')
parser.add_argument('--skip-zplug', action='store_true')
args = parser.parse_args()

################# BEGIN OF FIXME #################

# Task Definition
# (path of target symlink) : (location of source file in the repository)

tasks = {
    # SHELLS
    '~/.bashrc' : 'bashrc',
    '~/.screenrc' : 'screenrc',

    # VIM
    '~/.vimrc' : 'vim/vimrc',
    '~/.vim' : 'vim',
    '~/.vim/autoload/plug.vim' : 'vim/bundle/vim-plug/plug.vim',

    # NeoVIM
    '~/.config/nvim' : 'nvim',

    # GIT
    '~/.gitconfig' : 'git/gitconfig',
    '~/.gitignore' : 'git/gitignore',

    # ZSH
    '~/.zgen'     : 'zsh/zgen',
    '~/.zsh'      : 'zsh',
    '~/.zlogin'   : 'zsh/zlogin',
    '~/.zlogout'  : 'zsh/zlogout',
    '~/.zpreztorc': 'zsh/zpreztorc',
    '~/.zprofile' : 'zsh/zprofile',
    '~/.zshenv'   : 'zsh/zshenv',
    '~/.zshrc'    : 'zsh/zshrc',

    # Bins
    '~/.local/bin/dotfiles' : 'bin/dotfiles',
    '~/.local/bin/fasd' : 'zsh/fasd/fasd',
    '~/.local/bin/is_mosh' : 'zsh/is_mosh/is_mosh',
    '~/.local/bin/imgcat' : 'bin/imgcat',
    '~/.local/bin/imgls' : 'bin/imgls',
    '~/.local/bin/fzf' : '~/.fzf/bin/fzf', # fzf is at $HOME/.fzf

    # X
    '~/.Xmodmap' : 'Xmodmap',

    # GTK
    '~/.gtkrc-2.0' : 'gtkrc-2.0',

    # tmux
    '~/.tmux'     : 'tmux',
    '~/.tmux.conf' : 'tmux/tmux.conf',

    # .config
    '~/.config/terminator' : 'config/terminator',
    '~/.config/pudb/pudb.cfg' : 'config/pudb/pudb.cfg',

    # pip and python
    #'~/.pip/pip.conf' : 'pip/pip.conf',
    '~/.pythonrc.py' : 'python/pythonrc.py',
    '~/.pylintrc' : 'python/pylintrc',
    '~/.condarc' : 'python/condarc',
    '~/.config/pycodestyle' : 'python/pycodestyle',
}


from distutils.spawn import find_executable


post_actions = [
    '''# Check whether ~/.vim and ~/.zsh are well-configured
    for f in ~/.vim ~/.zsh ~/.vimrc ~/.zshrc; do
        if ! readlink $f >/dev/null; then
            echo -e "\033[0;33m\
WARNING: $f is not a symbolic link to ~/.dotfiles. \
You may want to remove your local file and try again?\033[0m"
        else
            echo "$f --> $(readlink $f)"
        fi
    done
    ''',

    # zgen installation
    '''# Update zgen modules and cache (the init file)
    zsh -c "
        source ${HOME}/.zshrc                   # source zplug and list plugins
        if ! which zgen > /dev/null; then
            echo -e '\033[0;31m\
ERROR: zgen not found. Double check the submodule exists, and you have a valid ~/.zshrc!\033[0m'
            ls -alh ~/.zsh/zgen/
            ls -alh ~/.zshrc
            exit 1;
        fi
        zgen reset
        zgen update
    "
    ''',

    # validate neovim package installation
    '''# neovim package needs to be installed
    if which nvim >/dev/null; then
        echo "neovim found at $(which nvim)"
        /usr/local/bin/python3 -c 'import neovim' || /usr/bin/python3 -c 'import neovim'
        rc=$?; if [[ $rc != 0 ]]; then
        echo -e '\033[0;33mNeovim requires 'neovim' package on the system python3. Please try:'
            echo -e '   /usr/local/bin/pip3 install neovim'
            echo -e '\033[0m'
        fi
    else
        echo "neovim not found, skipped"
    fi
    ''',

    # Run vim-plug installation
    {'install' : '{vim} +PlugInstall +qall'.format(vim='nvim' if find_executable('nvim') else 'vim'),
     'update'  : '{vim} +PlugUpdate  +qall'.format(vim='nvim' if find_executable('nvim') else 'vim'),
     'none'    : ''}[args.vim_plug],

    # Install tmux plugins via tpm
    '~/.tmux/plugins/tpm/bin/install_plugins',

    # Change default shell if possible
    r'''# Change default shell to zsh
    if [[ ! "$SHELL" = *zsh ]]; then
        echo -e '\033[0;33mPlease type your password if you wish to change the default shell to ZSH\e[m'
        chsh -s /bin/zsh && echo -e 'Successfully changed the default shell, please re-login'
    else
        echo '$SHELL is already zsh'
    fi
    ''',

    # Create ~/.gitconfig.secret file and check user configuration
    r'''# Create ~/.gitconfig.secret and user configuration
    if [ ! -f ~/.gitconfig.secret ]; then
        cat > ~/.gitconfig.secret <<EOL
# vim: set ft=gitconfig:
EOL
    fi
    if ! git config --file ~/.gitconfig.secret user.name 2>&1 > /dev/null; then echo -ne '
    \033[1;33m[!] Please configure git user name and email:
        git config --file ~/.gitconfig.secret user.name "(YOUR NAME)"
        git config --file ~/.gitconfig.secret user.email "(YOUR EMAIL)"
\033[0m'
    fi
    ''',
]

################# END OF FIXME #################

def _wrap_colors(ansicode):
    return (lambda msg: ansicode + str(msg) + '\033[0m')
GRAY   = _wrap_colors("\033[0;37m")
WHITE  = _wrap_colors("\033[1;37m")
RED    = _wrap_colors("\033[0;31m")
GREEN  = _wrap_colors("\033[0;32m")
YELLOW = _wrap_colors("\033[0;33m")
CYAN   = _wrap_colors("\033[0;36m")
BLUE   = _wrap_colors("\033[0;34m")


import os
import sys
import subprocess

try:
    from builtins import input   # python3
except ImportError:
    input = raw_input     # python2
from signal import signal, SIGPIPE, SIG_DFL
from optparse import OptionParser
from sys import stderr

def log(msg, cr=True):
    stderr.write(msg)
    if cr:
        stderr.write('\n')


# get current directory (absolute path)
current_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(current_dir)

# check if git submodules are loaded properly
stat = subprocess.check_output("git submodule status --recursive",
                               shell=True, universal_newlines=True)
submodule_issues = [(l.split()[1], l[0]) for l in stat.split('\n') if len(l) and l[0] != ' ']

if submodule_issues:
    stat_messages = {'+': 'needs update', '-': 'not initialized', 'U': 'conflict!'}
    for (submodule_name, submodule_stat) in submodule_issues:
        log(RED("git submodule {name} : {status}".format(
            name=submodule_name,
            status=stat_messages.get(submodule_stat, '(Unknown)'))))
    log(RED(" you may run: $ git submodule update --init --recursive"))

    log("")
    log(YELLOW("Do you want to update submodules? (y/n) "), cr=False)
    shall_we = (input().lower() == 'y')
    if shall_we:
        git_submodule_update_cmd = 'git submodule update --init --recursive'
        # git 2.8+ supports parallel submodule fetching
        try:
            git_version = str(subprocess.check_output("""git --version | awk '{print $3}'""", shell=True))
            if git_version >= '2.8': git_submodule_update_cmd += ' --jobs 8'
        except Exception as e:
            pass
        log("Running: %s" % BLUE(git_submodule_update_cmd))
        subprocess.call(git_submodule_update_cmd, shell=True)
    else:
        log(RED("Aborted."))
        sys.exit(1)


for target, source in sorted(tasks.items()):
    # normalize paths
    source = os.path.join(current_dir, os.path.expanduser(source))
    target = os.path.expanduser(target)

    # bad entry if source does not exists...
    if not os.path.lexists(source):
        log(RED("source %s : does not exist" % source))
        continue

    # if --force option is given, delete and override the previous symlink
    if os.path.lexists(target):
        is_broken_link = os.path.islink(target) and not os.path.exists(os.readlink(target))

        if args.force or is_broken_link:
            if os.path.islink(target):
                os.unlink(target)
            else:
                log("{:50s} : {}".format(
                    BLUE(target),
                    YELLOW("already exists but not a symbolic link; --force option ignored")
                ))
        else:
            log("{:50s} : {}".format(
                BLUE(target),
                GRAY("already exists, skipped")
            ))

    # make a symbolic link if available
    if not os.path.lexists(target):
        try:
            mkdir_target = os.path.split(target)[0]
            os.makedirs(mkdir_target)
            log(GREEN('Created directory : %s' % mkdir_target))
        except:
            pass
        os.symlink(source, target)
        log("{:50s} : {}".format(
            BLUE(target),
            GREEN("symlink created from '%s'" % source)
        ))

for action in post_actions:
    if not action:
        continue
    log(CYAN('\nExecuting: ') + WHITE(action.strip().split('\n')[0]))
    subprocess.call(['bash', '-c', action],
                          preexec_fn=lambda: signal(SIGPIPE, SIG_DFL))

log("\n" + GREEN("You are all set! "))
log("- Please restart shell (e.g. `exec zsh`) if necessary.")
log("- To install some packages locally (e.g. neovim, tmux), try `dotfiles install`")
