# CRM API
## Getting started
The API is implemented in python with the flask framework.

 **Check the [design.md file for detailed documentation on the API](design.md).**

There is a **debugging** and production docker configuration. The [compose-dev.yml](compose-dev.yml) builds the `dev` target for local development running in a docker container. It runs it with the `debugpy` debugger, which you can attach to on port `5678`. You can use the launch configuration in [.vscode/launch.json](.vscode/launch.json). To start the development environment you can run the bash script [start_dev.sh](start_dev.sh) and to stop it you can run [stop_dev.sh](stop_dev.sh). This spins up the docker container for the app and continually tries to attach to the log output. To get out you have to `Ctrl-C` twice, and if you need to stop the container, you can run [stop_dev.sh](stop_dev.sh). Hot reload is implemented by restarting the container every time there is a change to the filesystem. However, you need to re-attach your debugger. Breakpoints and the debug console are working on VSCode.

For **production** there is [docker-compose.yml](docker-compose.yml), it runs the API using [gunicorn](https://gunicorn.org/) as the WSGI server.

## Installation
Even though the development environment runs in  a container, if we want our IDE to be aware of the different python modules, and if we want to run various commands without spinning up a container, we need to install the packages locally. It's best to create a virtual environment, for example using virtualenv at the repository root:
```bash
mkvirtualenv crmapi -p /usr/bin/python3
```
Then install the packages via pip:
```bash
pip install -r requirements.txt
```
## Setting up the configuration file
There is both [config_dev.py](config_dev.py) and [config_prod.py](config_prod.py) configuration files. One for each environment. Please modify the variables according to your liking.
## Creating the database
To create the database for development, you need to run the following command in the root directory:
```bash
ENV=DEV; flask --app app init-db
```
This will create a SQLite database according to the values in your configuration file. It will also create the users `marduk` and `human`. Check the file [app/db.py](app/db.py) for their passwords. Note that in production, the `marduk` user uses the password set in the [config_prod.py](config_prod.py) file.
## Running the environment
Run:
```bash
./start_dev.sh
```
You should see flask's log output. Attach to the debugger, for example with VSCode. Breakpoints and the debug console should work. Hot reload is implemented by restarting the container and reattaching the debugger manually.

Should you need to stop the container, do a double `Ctrl-C` and run:
```bash
./stop_dev.sh
```
to stop the container.

Alternatively, you can run the application directly on your system without docker. Take a look at the [Dockerfile for running the commands](Dockerfile). Currently, this is more pragmatic if you are using the hot-reload feature a lot.
## Production environment
Follow the getting started guide for the development environment with the following modifications:
- the file [config_prod.py](config_prod.py) needs to be setup for the production environment. Make sure to change the **administrator password** and the **secret key** variables
- there is no mounting of repository files like in the debugging container. **Two volumes** are created instead, one for the database and another for the static files (customer profile pictures), and they are mounted in the corresponding folders.

There are a few missing features from the production environment, namely:
- More scalable persistence, like PostgreSQL instead of SQLite
- Load balancer and better static file serving via NGINX
- HTTPs, certificate from [Let's Encrypt](https://letsencrypt.org/) and automatic renewal via [Certbot](https://certbot.eff.org/)