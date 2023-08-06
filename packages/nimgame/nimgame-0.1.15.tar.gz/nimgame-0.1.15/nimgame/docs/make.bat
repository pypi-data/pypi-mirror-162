@ECHO OFF

REM Temporarily save the current dir
pushd %~dp0

REM the sphinx build command name could come from an env variable, otherwise the default
if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
REM Theoretically, other env vars could be set, but actually ignored and defaults are used 
set SOURCEDIR=.
set BUILDDIR=_build
set SPHINXOPTS=-E

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

REM If builder is missing, the help message is displayed
if "%1" == "" goto help

REM Do the build
%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
REM Restore the current dir
popd
