# aiobaro

Aiobaro is a Python client implementation for communicating with Matrix.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install aiobaro
```

## Usage

```python
from aiobaro.core import MatrixClient
client = MatrixClient("http://localhost:8008")
response = await client.login_info()
assert response.ok
response.json()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### Docker setup
```bash
docker-compose up -d
docker exec -it matrix register_new_matrix_user \
        http://localhost:8008 \
        -c /data/homeserver.yaml \
        -u admin -p ChangeMe --admin
```

* [Matrix admin](http://localhost:8080/#/login)
* [Matrix OpenApi](https://matrix.org/docs/api/client-server/#/)

### Python setup

Use the package manager [poetry](https://python-poetry.org/)
```bash
git clone https://github.com/oukone/aiobaro.git && cd aiobaro
poetry config virtualenvs.in-project true
poetry shell
poetry install
pre-commit install
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
