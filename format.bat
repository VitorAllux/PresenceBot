@echo off
autoflake --remove-all-unused-imports --in-place --recursive .
isort .
black .
flake8 .
for /R %%f in (*.py) do pylint %%f
