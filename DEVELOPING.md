# Guide to contribute to this repository

## Prerequisite

1. python3
2. pip3
3. virtualenv
    ```shell
    pip3 install virtualenv
    ```

## Steps to setup dev environment

1. Create a python3 virtual environment
    ```shell
    virtualenv .venv -p python3
    ```
2. Activate the virtual environment created in step 1
    ```shell
    source .venv/bin/activate
    ```
3. Install `setuptools` to package code and `black` to format python code
    ```shell
    pip3 install setuptools black
    ```
4. Install libraries in file requirements.txt
    ```shell
    pip3 install -r requirements.txt
    ```

## Steps to install the CLI to virtual environment and run it

1. Run command to install CLI in editable mode
    ```shell
    pip3 install -e .
    ```
2. Verify the CLI
    ```shell
    which aito
    ```
3. Run `aito` command
    ```shell
    aito
    ```

## Steps to package and distribute CLI to TestPyPI

1. Install `build` to generate distribution packages and `twine` to distribute package to PyPI
    ```shell
    pip3 install build twine
    ```
2. Run `build` command as the root folder, where file `pyproject.toml` is located
    ```shell
    rm -rf dist
    python3 -m build
    ```
    After that command, we will have `tar.gz` and `.whl` files in `dist` folder

3. Register an account in TestPyPI and create an API token with `Entire account` scope
4. Using twine to upload the distribution packages created in step 2 to TestPyPI
    ```shell
    twine upload --repository testpypi --skip-existing dist/*
    ```
    `--repository` used to choose upload to PyPI or TestPyPI, `--skip-existing` if we want to distribute further versions of the cli.

    You will be prompted for a username and password. For the username, use `__token__`. For the password, use the token value, including the pypi- prefix.
5. Using another virtual environment and install the `aitomatic-cli` using pip to verify that it works
    ```shell
    deactivate
    virtualenv .venv-test -p python3
    source .venv-test/bin/activate
    pip3 install -i https://test.pypi.org/simple/ aitomatic
    ```

## Steps to package and distribute CLI to PyPI

Similar to steps to distribute to TestPyPI, except:
- Don't need to specify `--repository` when running twine command
- Don't need to specify `-i` when running pip install command

## Temporary: If the deploy command failed due to change in service api. Update api base:

1. Clone https://github.com/aitomatic/ai-cloud
2. Follow instruction in `infrastructure/DEVELOPING.md` and select `dev` stack
3. Get the service host name
    ```shell
    pulumi stack select dev
    pulumi stack output kodaServiceHostname
    ```
4. Set AI_CLI_API_BASE env var to 
    ```shell
    export AI_CLI_API_BASE = "http://" + <hostname from step 3>
    ```
