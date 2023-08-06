from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Error(BaseModel):
    reasons: list[str]
    message: str


sample_error = [
    {"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing"},
    {"loc": ("body", "domain"), "msg": "field required", "type": "value_error.missing"},
    {
        "loc": ("body", "firstName"),
        "msg": "field required",
        "type": "value_error.missing",
    },
    {
        "loc": ("body", "acceptedTermsAndConditions"),
        "msg": "field required",
        "type": "value_error.missing",
    },
    {
        "loc": ("body", "acceptedGdprTerms"),
        "msg": "field required",
        "type": "value_error.missing",
    },
    {
        "loc": ("body", "acceptedCookiePolicy"),
        "msg": "field required",
        "type": "value_error.missing",
    },
    {"loc": ("body", "now"), "msg": "field required", "type": "value_error.missing"},
]


def process_pydantic_validation(v):
    def get_loc(d):
        return d.get("loc", (None,))[0]

    def get_type(d):
        return d.get("type", ".").split(".")[1]

    return list(map(lambda x: f"{get_loc(x)}:{get_type(x)}", v))


def return_error(msg: str, reasons: list[str]):
    return {"err": Error(message=msg, reasons=reasons)}


def json_http(status_code, content):
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))


def json_http_200(content):
    return json_http(200, content)


def json_http_400(msg, reasons):
    return json_http(400, return_error(msg, reasons))


def json_http_403(msg, reasons):
    return json_http(403, return_error(msg, reasons))


def json_http_404(msg, reasons):
    return json_http(404, return_error(msg, reasons))


def json_http_500(msg, reasons):
    return json_http(500, return_error(msg, reasons))


def json_http_200_with_cookie(content, key, value, max_age, secure, httponly):
    response = json_http(200, content)
    response.set_cookie(
        key=key, value=value, max_age=max_age, secure=secure, httponly=httponly
    )
    return response
