# devgrid

[![Pylint](https://github.com/BRomano/devgrid/actions/workflows/pylint.yml/badge.svg)](https://github.com/BRomano/devgrid/actions/workflows/pylint.yml)

## 

* I have used all technologies you asked to be used
  1. Python and flask framework
  2. pytest for automation tests
  3. schematics for modeling data 
  4. And docker and Docker compose to build everything

* The cache_ttl and default_max_number are enviroment variables, and can be setted on docker-compose.yml

* I have used Flask-caching for cache solution
* Also I have used flasgger for documentation, it can be seen on /apidocs
* And pycountry to convert country ISO 3166-1 Alpha 2 to Alpha 3

The application was deployed on [API](http://159.223.180.98:8080/apidocs/)
> To run automated tests
````shell
pytest
````
> To run the project need to run, it will be running on 8080
````shell
docker-compose up
````
