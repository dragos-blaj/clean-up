# CleanUp project in Flask



## Install

```shell script
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt -r requirements-dev.txt
$ pip3 install -e .
```


## Running

Running the application.

```shell script
$ docker-compose up -d

# first time only
$ FLASK_APP=cleanup flask init-db
$ FLASK_APP=cleanup flask add-user manager pass
```

Running the tests.

```shell script
$ pytest
```

## Others

Print the routes to see all available endpoints.

```shell script
$ flask routes
```
