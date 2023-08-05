## Set up
```
# create virtual environment
python3 -m virtualenv venv
```

```
# activate virtual environment
source venv/bin/activate
```

```
# install dependencies
pip install -r requirements.txt
```

## Build the module
**Note**: make sure version is bumped in setup.py before building

```
# build the dist/ folder
python setup.py sdist
```

```
# upload to PyPi using twine
twine upload dist/*
```