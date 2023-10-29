Pyramid Scaffold
================

Getting Started
---------------

- Change directory into your newly created project if not already there. Your
  current directory should be the same as this README.txt file and setup.py.

    cd pyramid_scaffold

- Create a Python virtual environment, if not already created.

    python3 -m venv env

- Upgrade packaging tools, if necessary.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements. OPTIONAL: if there's any error just ignore it.

    env/bin/pip install -e ".[testing]"

- Initialize and upgrade the database using Alembic. REMEMBER to create the database first "shopify"

    - Generate your first revision. it will make the database

        env/bin/alembic -c development.ini revision --autogenerate -m "init"

    - Upgrade to that revision. (migrate the model to the database)

        env/bin/alembic -c development.ini upgrade head

- Load default data into the database using a script.

    env/bin/initialize_pyramid_scaffold_db development.ini

- Run your project's tests. OPTIONAL: if there's any error just ignore it.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini