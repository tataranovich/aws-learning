#!/bin/bash
docker run --name simple-app-service -tid -p 80:80 -v /simple-app:/var/www/html php:7.0-apache