# sparta-memcached

Sparta memcached library.

## Usage

See [here](/USAGE.md).

## Dependency management

You need to have [virtualenv](https://docs.python.org/3/tutorial/venv.html) installed globally. In case you don't, run:

```bash
pip install virtualenv
```

Create and activate a **_virtualenv_** (name it `.venv`).

```bash
python -m venv .venv
source .venv/bin/activate
```

> You should now see the prefix `(.venv)` in your terminal prompt. This means the virtualenv is active.

## Install locally

Install default and test requirements (assure `.venv` is active).

```shell
pip install -e .[test]
```

Run tests.

```shell
python -m pytest
```

## Publish on [Pypi](https://pypi.org/project/sparta-memcached/)

A [cloud build](https://console.cloud.google.com/cloud-build/triggers?project=spartaproduct&pageState=(%22triggers%22:(%22f%22:%22%255B%257B_22k_22_3A_22Repository_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22Spartan-Approach%252Fsparta-memcached_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22repository_22%257D%255D%22)))
will publish the package on [pypi.org](https://pypi.org/project/sparta-memcached/) whenever a new tag is pushed to our
git repo.

```shell
./scripts/rollout_version.sh [patch|minor|major]
```

> When prompt `Push changes?`, type `y`.

Alternatively, you can publish manually.

```shell
./scripts/publish.sh --username spartanaproach --password ***
```
