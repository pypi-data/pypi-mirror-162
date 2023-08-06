# JWT Token Parser
A small library to parse jwt token

### Installation
```
pip install jwt-token-parser-test
```

### Get started
How to get payload from jwt token:

```Python
from jwt_token_parser_test_1 import JWTTokenParser

# Instantiate a Multiplication object
jwt_parser = JWTTokenParser(key='SECRET_KEY')

# Call the multiply method
result = jwt_parser.get_payload_by_access_token()
```