# JWT Token Parser
A small library to parse jwt token

### Installation
```
pip install jwt-token-parser
```

### Get started
How to get payload from jwt token:

```Python
from jwt_token_parser import JWTTokenParser

# Instantiate a Multiplication object
jwt_parser = JWTTokenParser()

# Call the multiply method
result = jwt_parser.get_payload_by_access_token(key='SECRET_KEY')
```