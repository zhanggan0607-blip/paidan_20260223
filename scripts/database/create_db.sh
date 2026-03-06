#!/bin/bash
su - postgres -c "psql -c \"CREATE USER postgres WITH PASSWORD '123456';\""
su - postgres -c "psql -c \"CREATE DATABASE tq OWNER postgres;\""
