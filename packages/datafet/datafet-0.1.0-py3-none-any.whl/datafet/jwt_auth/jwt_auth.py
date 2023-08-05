import time

import jwt
from ecdsa import SigningKey, VerifyingKey
from pydantic import BaseModel, EmailStr

DEFAULT_ALGORITHM = "ES256"


class JwtParam(BaseModel):
    email: EmailStr
    firstName: str
    domain: str


def create_jwt(
    jwt_param: JwtParam,
    signing_key: SigningKey,
    audience: str,
    issuer: str,
    exp_days=2,
    algorithm=DEFAULT_ALGORITHM,
):

    now = int(time.time())
    expiry = now + exp_days * 24 * 60 * 60
    return jwt.encode(
        {
            "email": jwt_param.email,
            "firstName": jwt_param.firstName,
            "domain": jwt_param.domain,
            "aud": audience,
            "exp": expiry,
            "iss": issuer,
            "iat": now,
            "nbf": now,
        },
        signing_key.to_pem(),
        algorithm=algorithm,
    )


def create_empty_jwt(
    signing_key: SigningKey, audience: str, issuer: str, algorithm=DEFAULT_ALGORITHM
):

    now = int(time.time())
    return jwt.encode(
        {
            "aud": audience,
            "exp": now,
            "iss": issuer,
            "iat": now,
            "nbf": now,
        },
        signing_key.to_pem(),
        algorithm=algorithm,
    )


def decode_jwt(
    jwt_string: str, verifying_key: VerifyingKey, algorithm=DEFAULT_ALGORITHM
):
    return jwt.decode(
        jwt_string.encode("utf-8"),
        verifying_key.to_pem(),
        algorithms=[algorithm],
        audience="Depoxy",
    )


def is_valid_jwt(jwt_string: str):
    try:
        decoded = decode_jwt(jwt_string)
        if decoded:
            return True
    except Exception as _ex:
        return False


def get_user_email(jwt_string: str):
    decoded = decode_jwt(jwt_string)
    if decoded:
        return decoded.get("email")
    return None


def who_am_i(jwt_string: str, verifying_key: VerifyingKey):
    result = decode_jwt(jwt_string, verifying_key)
    if result:
        jwt_param = JwtParam(
            email=result.get("email"),
            firstName=result.get("firstName"),
            domain=result.get("domain"),
        )
        if jwt_param.email and jwt_param.firstName and jwt_param.domain:
            return jwt_param
        else:
            raise Exception(f"JWT token is missing mandatory field(s) {jwt_param}")
    else:
        raise Exception("Invalid JWT token")
