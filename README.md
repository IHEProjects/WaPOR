# Python

```
print(shape)  # TODO, 20190912, QPan, to delete
```

# Xarray

## chunk

* Don't use negative value
* Don't use "auto"

To calculate chunck size:

* Input
  * AETI(dtype=short(16bits=2bytes)).chunk[time=1, lat=1000, lon=1000]
  * Memory/timestep/all   = 2*(1*35915*16493)/1024/1024/1024 = 1.1gb
  * Memory/timestep/chunk = 2*(1*1000 *1000 )/1024/1024      = 1.9mb
* Output
  * Actual Evapotranspiration(dtype=float(32bits=4bytes)).chunk[time=1, lat=1996, lon=917]
  * Memory/timestep/all   = 4*(1*35915*16493)/1024/1024/1024 = 2.2gb
  * Memory/timestep/chunk = 4*(1*1996 *917  )/1024/1024      = 7.0mb

# Docker

* [Docker Osgeo GDAL](https://hub.docker.com/r/osgeo/gdal)
* [DockerImages](https://wiki.osgeo.org/wiki/DockerImages)
* [Docker Toolbox](https://docs.docker.com/toolbox/overview/)
* [Docker Community Edition](https://docs.docker.com/docker-for-windows/release-notes/)
* [Docker Volume Windows](https://stackoverflow.com/questions/33126271/how-to-use-volume-option-with-docker-toolbox-on-windows)

## BIOS Virtualization

Enable Virtualization in BIOS

## Setup shared folder with docker

### Windows 7, VirtualBox

Use toolbox to install docker, it will create VirtualBox default machine (boot2docker.iso)

VirtualBox -> Settings -> Shared Folders

Add

* Folder Path: D:\00-Template
* Folder Name: d/00-Template
* Auto-mount
* Make Permanent

Docker CMD

* docker-machine ssh
* ls /d/00-Template

### Windows 10, Hyper-V

## Docker-machine

```
docker-machine ls
NAME      ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER     ERRORS
default   *        virtualbox   Running   tcp://192.168.99.100:2376           v18.09.9

# docker-machine env
# export DOCKER_TLS_VERIFY="1"
# export DOCKER_HOST="tcp://192.168.99.100:2376"
# export DOCKER_CERT_PATH="C:\Users\qpa001\.docker\machine\machines\default"
# export DOCKER_MACHINE_NAME="default"
# export COMPOSE_CONVERT_WINDOWS_PATHS="true"
# # Run this command to configure your shell:
# # eval $("C:\Program Files\Docker Toolbox\docker-machine.exe" env)

docker-machine start default
docker-machine stop default
```

## Build and start docker

cmd window 1

```
cd D:\00-Template\Docker
docker build -t qpan/jupyter .
```

### Windows 7, VirtualBox

```
cd D:\00-Template
docker run -it --name jupyter -p 8888:8888 -v /d/00-Template:/notebooks qpan/jupyter
```

### Windows 10, Hyper-V

```
cd D:\00-Template
docker run -it --name jupyter -p 8888:8888 -v D:/00-Template:/notebooks qpan/jupyter
```

### Mac, Linux

```
cd /Volumes/QPan_T5/IHE/00-Template/
docker run -it --name jupyter -p 8888:8888 -v $(PWD):/notebooks qpan/jupyter

# docker run -d --name jupyter -p 8888:8888 -v $(PWD):/notebooks qpan/jupyter
```

## Access to runing docker

cmd window 2

```
docker exec -it jupyter bash

jupyter notebook list

cd /notebooks

gdalinfo --version
GDAL 3.1.0dev-650fc42f344a6a4c65f11eefc47c473e9b445a68, released 2019/08/25

python3 qpan_gdalwarp.py 
```

## Copy data to docker

```
docker cp /Volumes/QPan_T5/IHE/00-Template gdal:/
```

## Clean docker

```
docker system prune -f && docker volume prune -f && docker container prune -f
```

## Save docker images

```
docker save --output qpan_jupyter.tar qpan/jupyter
```

## Load docker images

```
docker load --input qpan_jupyter.tar
```
