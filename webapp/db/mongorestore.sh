#!/bin/bash

# Start MongoDB in the background
mongod --bind_ip_all &

# Wait for MongoDB to fully start
sleep 5

# Restore the dump
mongorestore --db PerfilPublicoAll --verbose /data/dump


