# Solarpark

Backend service for Solarpark.

## Installation

This project uses poetry for package management.

Run `make develop` to install all packages needed for running, testing and developing. To only install the required
packages for running the application run `make install`.

`make lint` will format your code and run a static analysis of your python code. If you installed the package with
`make develop` then the same checks will be run before commits.

## Running the project from vscode

Create `launch.json` in `/.vscode`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "env": {}
    }
  ]
}
```

Open `main.py` & press F5

Swagger Ui is now available on http://localhost:8000/docs

### Adding and updating packages

To update a package first install it with poetry (`poetry add <package>`). Then run `make update-dependencies` to update
the `requirements.txt` file which is used in the deploys.

To update packages in the project run `poetry update` followed by `make update-dependencies` and commit the changes.
