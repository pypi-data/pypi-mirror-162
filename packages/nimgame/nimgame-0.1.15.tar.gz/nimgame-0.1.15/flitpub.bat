@ECHO OFF

REM Script to execute publishing a new version (PyPi and ReadTheDocs)
REM Run this bat in its own directory as cwd

REM **********************************
REM Documentation
REM **********************************
REM Temporarily save the current dir, go down to project dir
pushd %~dp0
REM cd nimgame

REM autogen must see the import path in the env
SET PYTHONPATH=nimgame
REM Do the doc module auto-generate
REM sphinx-autogen -i nimgame/docs/index.rst

REM Restore the current dir
popd


REM **********************************
REM PyPi upload
REM **********************************
REM See https://flit.pypa.io/en/latest/cmdline.html#flit-publish
flit publish --pypirc .\.pypirc
