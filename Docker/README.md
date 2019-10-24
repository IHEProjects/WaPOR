# WaPOR

# BIOS Virtualization

Enable Virtualization in BIOS

# Docker

* [Docker Osgeo GDAL](https://hub.docker.com/r/osgeo/gdal)
* [DockerImages](https://wiki.osgeo.org/wiki/DockerImages)
* [Docker Toolbox](https://docs.docker.com/toolbox/overview/)
* [Docker Community Edition](https://docs.docker.com/docker-for-windows/release-notes/)
* [Docker Volume Windows](https://stackoverflow.com/questions/33126271/how-to-use-volume-option-with-docker-toolbox-on-windows)

## Setup shared folder with docker

### Windows 7, VirtualBox

Use toolbox to install docker, it will create VirtualBox default machine (boot2docker.iso)

VirtualBox -> Settings -> Shared Folders

Add

* Folder Path: D:\WaPOR
* Folder Name: d/wateraccounting
* Auto-mount
* Make Permanent

Docker CMD

* docker-machine ssh
* ls /d/WaPOR

### Windows 10, Hyper-V

## Docker-machine

```
docker-machine ls
NAME      ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER     ERRORS
default   *        virtualbox   Running   tcp://192.168.99.100:2376           v18.09.9

docker-machine start default
docker-machine stop default
```

## Build and start docker

cmd window 1

```
cd D:\WaPOR\Docker
docker build -t quanpan302/ihe_projects_wapor .
```

### Windows 7, VirtualBox

```
cd D:\WaPOR
docker run -it --name WP-Dev -p 8888:8888 -v /d/WaPOR:/notebooks quanpan302/ihe_projects_wapor
```

```
cd D:\test
docker run -it --name WP-Test -p 8888:8888 -v /d/test:/notebooks quanpan302/ihe_projects_wapor
```

### Windows 10, Hyper-V

```
cd D:\WaPOR
docker run -it --name WP-Dev -p 8888:8888 -v D:/WaPOR:/notebooks quanpan302/ihe_projects_wapor
```

### Mac, Linux

```
cd /Volumes/QPan_T5/WaPOR/
docker run -it --name WP-Dev -p 8888:8888 -v $(PWD):/notebooks quanpan302/ihe_projects_wapor

# docker run -d --name WP-Dev -p 8888:8888 -v $(PWD):/notebooks quanpan302/ihe_projects_wapor
```

## Access to runing docker

cmd window 2

```
docker exec -it WP-Dev bash

jupyter notebook list

cd /notebooks

gdalinfo --version
GDAL 3.1.0dev-650fc42f344a6a4c65f11eefc47c473e9b445a68, released 2019/08/25

python3 wa_gdalwarp.py 
```

## Copy data to docker

```
docker cp /Volumes/QPan_T5/WaPOR gdal:/
```

## Clean docker

```
docker system prune -f && docker volume prune -f && docker container prune -f
```

## Save docker images

```
docker save --output wateraccounting_jupyter.tar quanpan302/ihe_projects_wapor
```

## Load docker images

```
docker load --input wateraccounting_jupyter.tar
```
