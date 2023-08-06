from fastapi.responses import JSONResponse
from .models.commons.exceptions import ServingHttpError


def __mk_response_body(code, message, data):
    return {"code": code, "message": message, "data": data}


def _mk_json_response(code, message, data, status_code):
    return JSONResponse(
        __mk_response_body(
            code,
            message,
            data,
        ),
        status_code=status_code,
    )


def success_response(body: dict, status_code: int = 200):
    if not isinstance(body, dict):
        raise ValueError("body must be a dict!")
    return _mk_json_response(0, "Success", body, status_code)


def failed_response(body: dict = None, message: str = None, status_code: int = 400):
    if body is None:
        body = {}
    if not isinstance(body, dict):
        raise ValueError("body must be a dict!")
    return _mk_json_response(-1, message if message else "Failed", body, status_code)


def failed_response_with_break(
    body: dict = None, message: str = None, status_code: int = 400
):
    if body is None:
        body = {}
    if not isinstance(body, dict):
        raise ValueError("body must be a dict!")

    raise ServingHttpError(
        status_code=status_code,
        detail=__mk_response_body(-1, message if message else "Failed", body),
    )


__all__ = ["success_response", "failed_response"]
