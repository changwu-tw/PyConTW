# Threshold Cryptography with Python

## Instrall SageMath via Docker


- [https://hub.docker.com/r/sagemath/sagemath](https://hub.docker.com/r/sagemath/sagemath)

```
$ git clone https://github.com/changwu-tw/PyConTW
$ cd PyConTW
$ docker pull sagemath/sagemath
$ docker run -p8888:8888 --name notebook \
      -v "$PWD":/home/sage/pycontw \
      sagemath/sagemath:latest sage-jupyter
$ docker stop notebook
```

## Notebooks

- Shamir Secret Sharing.ipynb
- ECDSA.ipynb
- Points on Elliptic Curves.ipynb


## Local development environment

- [Installation](Install_zh-TW.md)
