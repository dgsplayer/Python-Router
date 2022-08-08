#!/bin/sh

python3 --version
python3 -c "import platform; print(platform.architecture()[0])"
python3 -m pip --version
python3 -m pip install --upgrade pip

python3 -m pip install -U --user ortools

python3 -m pip show ortools

rm -rf dist dist.zip; mkdir dist

cp -rv libs/site-packages/* dist
# find "./libs/site-packages" -path "*.egg/*" -not -name "EGG-INFO" -maxdepth 2 -exec cp -r {} ./dist \;
find -not -name "*.png" -not -name "*.html" -not -name "*.json" -not -name "*.js" -not -name 'dist' -not -name 'libs' -not -name 'Dockerfile' -not -name 'package.sh' -mindepth 1 -maxdepth 1 -exec cp -r {} ./dist \;

chmod -R 755 ./dist

cd dist; zip -r ../dist.zip *
