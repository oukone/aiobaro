# aiobaro

Foobar is a Python library for dealing with word pluralization.

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

## Python setup

Use the package manager [poetry](https://python-poetry.org/)
```bash
git clone https://github.com/oukone/aiobaro.git && cd aiobaro
poetry shell
poetry install
```


## License
[MIT](https://choosealicense.com/licenses/mit/)
