# Simple E-commerce Backend

<p align="center" style="margin: 3em">
  <a href="https://github.com/fsiconha/simple-ecomm">
    <img src="simple-ecomm.png" alt="simple-ecomm"/ width="250">
  </a>
</p>

<p align="center">
    <em>Image obtained from www.flaticon.com/free-icon/ecommerce_1145012</em>
</p>

This project uses **Poetry** to dependencies management. But alternatively, you can set up and run the project using only **Conda**. Feel free to choose whichever way you like (;

## Using Poetry

### Set Up
```
$ git clone https://github.com/fsiconha/simple-ecomm.git
$ cd simple-ecomm
$ pip install poetry
$ poetry env use python
$ poetry install
```

### Run Unit Tests
```
$ poetry run python3 run_tests.py
```

### Start App
```
$ poetry run python3 run_app.py
```

### Access API Docs
```
http://127.0.0.1:5000/apidocs
```

## Using Conda

### Alternative set up 
```
$ git clone https://github.com/fsiconha/simple-ecomm.git
$ cd simple-ecomm
$ pip install anaconda
$ conda create -n simple-ecomm-env python=3.12
$ conda activate simple-ecomm-env
$ pip install -r requirements.txt
```

### Run Unit Tests
```
$ python3 run_tests.py
```

### Start App
```
$ python3 run_app.py
```

### Access API Docs
```
http://127.0.0.1:5000/apidocs
```
