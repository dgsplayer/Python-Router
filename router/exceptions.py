from flask import jsonify

class AppException(Exception):
    def __init__(self, reason, error_code="INTERNAL_SERVER_ERR", status_code=500, payload=None):
        super().__init__()
        self.reason = reason
        self.error_code = error_code
        self.status_code = status_code
        self.payload = payload

    def to_response(self):
        res_dict = self.payload or {}
        res_dict['reason'] = self.reason
        res_dict['error_code'] = self.error_code
        res = jsonify(res_dict)
        res.status_code = self.status_code
        return res

    @classmethod
    def validation_error(cls, error=None):
        return cls("Validation Error",
                   error_code="VALIDATION_ERR",
                   status_code=400,
                   payload={"fields": error.messages})

    @classmethod
    def no_route(cls):
        return cls("No router soluction found",
                   error_code="NO_ROUTE",
                   status_code=204)