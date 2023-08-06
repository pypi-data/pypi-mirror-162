About this pyscript_src_patched directory
=========================================
This is a patch to PyScript, so that it handles local file hierarchy.

Content
-------
This directory contains the downloaded `pyscriptjs/src` (not the full pyscript download).
Additionally, it contains the `pyscript.js` file, which is a transpile (TypeScript compile) of the .ts files and, therefore, is not part of the source.
However, it is still needed for offline execution, i.e. loading this locally patched .js from the HTML instead of the online
https://pyscript.net/alpha/pyscript.js.
So, whatever is changed in the .ts sources, the same changes appear in this local `pyscript.js`.

New feature
-----------
The original `<py-env>` can specify public packages and local modules (under the "paths" object).
In order to define the local package with its directory structure, this patch introduces a new object named "localpackage".
Its "packagebase" element states where the modules of the local package are based in the directory structure,
relative to the HTML file referring to it.
A "paths" element of the local package can state what sections of the package is to be loaded.
If this "paths" is missing, the full directory structure is loaded.
If "paths" lists directories, all modules under that directory (and recursively all sub-directories) are loaded.
If "paths" lists certain modules, only those modules are loaded from the local package.
Directories and modules can be mixed in the "paths" list.

.. note:: If the "paths" list is defined outside of the "localpackage" object, it works as before the patch,
i.e. it does not preserve the module location in the file structure and only will be importable by its single name.


Example
-------
::

    ├── mypackage
    │   ├── web
    │   │   ├── frontend
    │   │   │   ├── index.htm
    │   ├── main.py
    │   ├── dir1
    │   │   ├── mod1.py
    │   │   ├── mod2.py
    │   │   ├── subdir
    │   │   │   ├── mod2.py
    │   ├── dir2
    │   │   ├── mod1.py
    │   │   ├── mod2.py

In `/mypackage/web/frontened/index.html`, we have the following snippet::

    <py-env>
    - public-package-1
    - public-package-2
    - localpackage:
        packagebase: ../../
        paths:
        - main.py
        - dir1/subdir/mod2.py
        - dir2/mod2.py
    </py-env>

The packagebase is 2 levels up from the directory of index.html,  i.e. `/mypackage/web/frontened/../../` ==> `/mypackage/`.
This environment is now loaded with the the 3 modules.

The `main.py` can then import other modules from the local package naturally, with reference to their import paths:

.. code-block:: python

    from dir1.subdir import mod2 as mod2_of_subdir
    from dir2 import mod2 as mod2_of_dir2

.. role:: python(code)
   :language: python

.. note::
    * Not unique module file names (see `mod2` twice) is not an issue anymore.
    * Trying :python:`from dir2 import mod1` fails, because it was not loaded into the environment.


File "components/pyenv.ts" changes
----------------------------------
Method `connectedCallback()` of class PyEnv has a for loop to read the `<py-env>` content.
If it is a string, it is interpreted as a public package, as normal. Also, "paths" objects are interpreted as normal.

The new "localpackage" objects are handled in this patch.
"packagebase" is stored, if exists, otherwise it is considered as an empty path (i.e. the current directory).
The list of paths of this package are stored in the new "modules" list, instead of "paths".
"module" objects in the "modules" list have 2 elements. "path" element is the source path and the "base" element is the packagebase value.
In function `loadPaths()`, this "module" object is sent to function `loadFromFile()` of the "interpreter.ts" instead of the sole path string.


File "interpreter.ts"
---------------------
In `loadFromFile()`, instead of receiving the sole path string, the "module" object is received, which contains the path as well as the package base.
All execution is done in the Python code and no need for the path-less filename calculation in getLastPath() of "utils.ts" anymore.
Using the Python standard pathlib package, the target path is calculated, i.e. where to store the fetched modules.
If the path requires subdirectories, they are automatically created.
