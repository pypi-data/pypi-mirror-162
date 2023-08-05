# julia_project_basic

This Python package provides functions to check if a Julia project is properly installed and ready to use.

It ensures that registries and packages are installed. It ensures that PyCall.jl is
installed, built, and that the libpython of the running python interpreter is compatible with
the one used to build PyCall.jl

## Install

```sh
pip install julia_project_basic
```

### Examples

#### Simplest use

```python
import os
import julia_project_basic
os.chdir("/path/to/julia/project/")
julia_project_basic.ensure_project_ready()
```

You can also use `ensure_project_ready_fix_pycall` which does everything
`ensure_project_ready` does and also checks whethr `PyCall.jl` is installed,
built and is compatible with the currently running python interpreter.
`PyCall.jl` will be built if it is not already.
If it is incompatible, the user will be given a choice between recompiling `PyCall.jl` or
installing everything to a "private" depot.

In the case that the Julia project is installed and ready to use, `ensure_project_ready`
takes about 200 micro s to run. And `ensure_project_ready_fix_pycall` takes about
200 ms to run. The factor of 1000 is due to starting a julia process and running a bit
of julia code in the second case.

#### Options

See the docstrings for `ensure_project_ready` and `ensure_project_ready_fix_pycall` for
a description of arguments.


#### Details

`ensure_project_ready` does the following

- checks if the `Manifest.toml` (or `JuliaManifest.toml`) exists and is newer than `Project.toml`.
  It checks if a few directories in the Julia depot are present. It optionally checks if additional
  registries are installed. It optionally checks if a supplied list of packages are in the `Project.toml`.
  If any of these checks fail, then
  The following steps are taken to install registries, packages, etc. and to run `Pkg.instantiate`.

- Optionally, registries are installed.

- Optionally, packages are added to the project (version specs are not supported)

- The project is instantiated.


`ensure_project_ready_fix_pycall` additionally checks `PyCall.jl` and tries to fix it if necessary.

