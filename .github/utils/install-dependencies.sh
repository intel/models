#!/bin/bash


if [ -e "requirements.txt" ] ; then
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ] ; then
        echo "Error installing dependencies from requirements.txt"
    else
        echo "Requirements installed from requirements.txt"
    fi
elif [ -e "pyproject.toml" ] ; then
    which poetry
    if [ $? -ne 0 ] ; then
        #install poetry
        curl -o poetry-install.py https://install.python-poetry.org
        python3 poetry-install.py --yes --force
        if [ $? -ne 0 ] ; then
            echo "Error installing poetry to manage dependencies"
            exit 1
        else
            source ~/.bashrc
            poetry install
            if [ $? -ne 0 ] ; then
                echo "Error installing dependencies with poetry."
            else
                echo "Dependencies installed with poetry."
            fi
        fi
    fi
fi
