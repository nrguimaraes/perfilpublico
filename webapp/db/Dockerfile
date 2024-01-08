#
# MongoDB Dockerfile
#
# https://github.com/dockerfile/mongodb
#

# Pull base image.
FROM mongo:5.0.17


COPY ./PerfilPublicoMongoDB /dump

RUN mongorestore

