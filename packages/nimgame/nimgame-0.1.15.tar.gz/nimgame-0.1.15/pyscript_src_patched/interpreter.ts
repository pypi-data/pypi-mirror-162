import { getLastPath } from './utils';
import type { PyodideInterface } from './pyodide';
// eslint-disable-next-line
// @ts-ignore
import pyscript from './pyscript.py';

let pyodideReadyPromise;
let pyodide;

const loadInterpreter = async function (indexUrl: string): Promise<PyodideInterface> {
    console.log('creating pyodide runtime');
    // eslint-disable-next-line
    // @ts-ignore
    pyodide = await loadPyodide({
        // indexURL: indexUrl,
        stdout: console.log,
        stderr: console.log,
        fullStdLib: false,
    });

    // now that we loaded, add additional convenience functions
    console.log('loading micropip');
    await pyodide.loadPackage('micropip');

    console.log('loading pyscript...');
    await pyodide.runPythonAsync(pyscript);

    console.log('done setting up environment');
    return pyodide;
};

const loadPackage = async function (package_name: string[] | string, runtime: PyodideInterface): Promise<void> {
    if (package_name.length > 0){
        const micropip = pyodide.globals.get('micropip');
        await micropip.install(package_name);
        micropip.destroy();
    }
};

const loadFromFile = async function (module: string, runtime: PyodideInterface): Promise<void> {
    await runtime.runPythonAsync(
        `
            from pyodide.http import pyfetch
            from js import console
            import pathlib
            
            source_relative_filename = "` + module.path + `"
            source_relative_path = pathlib.Path(source_relative_filename)
            packagebase = pathlib.Path("` + module.base + `")
            try:
                target_path = source_relative_path.relative_to(packagebase)
            except ValueError as err:
                console.warn(f"PyScript: py-env error: {err}")
                raise
            try:
                response = await pyfetch(source_relative_filename)
            except Exception as err:
                console.warn("PyScript: Access to local files (using 'Paths:' in py-env) is not available when directly opening a HTML file; you must use a webserver to serve the additional files. See https://github.com/pyscript/pyscript/issues/257#issuecomment-1119595062 on starting a simple webserver with Python.")
                raise(err)
            content = await response.bytes()
            
            # Create directory structure, if needed
            for pathelem in [p for p in target_path.parents][::-1]:
                if not pathelem.is_dir():
                    cwd = pathlib.Path.cwd()
                    abspath = (cwd / pathelem).resolve()
                    try:
                        abspath.relative_to(cwd)
                    except ValueError as err:
                        console.warn(f"PyScript: py-env error: {pathelem} tries to go up beyond the package base")
                        raise
                    console.log(f"Creating {abspath}")
                    try:
                        pathelem.mkdir()
                    except Exception as err:
                        console.warn("PyScript: mkdir error: f{repr(err)}")
                        raise
            
            target_filename = str(target_path)
            with open(target_filename, "wb") as f:
                f.write(content)
            console.log(f"Stored {target_filename}")
        `,
    );
};

export { loadInterpreter, pyodideReadyPromise, loadPackage, loadFromFile };
