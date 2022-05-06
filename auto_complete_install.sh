#!/usr/bin/env bash
if [[ $(basename $SHELL) = 'bash' ]];
then
    echo "Installing bash autocompletion..."
    echo 'eval "$(_AITO_COMPLETE=bash_source aito)"' > ~/.aito-autocompletion.sh
    if [ -f ~/.bashrc ];
    then
        grep -q 'aito-autocompletion' ~/.bashrc
        if [[ $? -ne 0 ]]; then
            echo "" >> ~/.bashrc
            echo "source ~/.aito-autocompletion.sh" >> ~/.bashrc
        fi
    fi
elif [[ $(basename $SHELL) = 'zsh' ]];
then
    echo "Installing zsh autocompletion..."
    echo 'eval "$(_AITO_COMPLETE=zsh_source aito)"' > ~/.aito-autocompletion.sh
    if [ -f ~/.zshrc ];
    then
        grep -q 'aito-autocompletion' ~/.zshrc
        if [[ $? -ne 0 ]]; then
            echo "" >> ~/.zshrc
            echo "autoload bashcompinit" >> ~/.zshrc
            echo "bashcompinit" >> ~/.zshrc
            echo "source ~/.aito-autocompletion.sh" >> ~/.zshrc
        fi
    fi
fi
