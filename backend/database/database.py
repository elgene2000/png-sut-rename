from ats_logging import get_logger
from typing import Dict, List, Union

logger = get_logger(__name__, print_logs=False)


import models
from backend import (Endpoint, RequestError)
from requests import Response


def suppress_errors(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RequestError:
            logger.exception("Exception suppressed by controller, returning None.")
            return None

    return wrapper


class DatabaseController:
    def __init__(self, model: models.Model, endpoint: Endpoint):
        self.model = model
        self.endpoint = endpoint

    def _get_model_objs(self, data):
        model_objs = None
        if isinstance(data, list):
            model_objs = []
            for item in data:
                model_obj = self.model()
                model_obj.from_db = True
                model_obj.from_dict(item)
                model_objs.append(model_obj)
        elif data:
            model_obj = self.model()
            model_obj.from_db = True
            model_obj.from_dict(data)
            model_objs = model_obj
        return model_objs

    @suppress_errors
    def query(self, **kwargs) -> Union[models.Model, List[models.Model]]:
        response = self.endpoint.get(**kwargs)
        if "return_record_count" in kwargs:
            query_result = {
                "data": self._get_model_objs(response["data"]),
                "record_count": response["record_count"],
                "last_page": response["last_page"],
            }
        else:
            query_result = response
        return query_result

    def get(self, **kwargs) -> Union[models.Model, List[models.Model]]:
        return self.query(**kwargs)

    def update(
        self,
        model_obj: Union[models.Model, Dict],
        race_condition_check=False,
        return_response=False,
        **kwargs
    ) -> Union[Dict, List, Response]:
        clear_unused = True
        if isinstance(model_obj, Dict):
            data = model_obj
            kwargs["identifier"] = data.pop("id", None)
            clear_unused = False
        elif (
            isinstance(model_obj, list) and model_obj and isinstance(model_obj[0], Dict)
        ):
            data = model_obj
            kwargs["identifier"] = None
        else:
            # race_condition_check is only supported on certain endpoints
            # if specified on unsupported endpoint will be ignored
            data = model_obj.to_dict(include_nested=False, only_modified=True)
            kwargs["identifier"] = model_obj.id
        if race_condition_check is True:
            data["expected_state_before_update"] = model_obj.snapshot
        res = self.endpoint.put(
            clear_unused=clear_unused,
            return_response=return_response,
            data=data,
            **kwargs
        )
        return res

    def put(
        self,
        model_obj: Union[models.Model, Dict],
        race_condition_check=False,
        return_response=False,
        **kwargs
    ) -> Union[Dict, List, Response]:
        return self.update(
            model_obj, race_condition_check, return_response=return_response, **kwargs
        )

    def insert(
        self,
        model_obj: Union[
            models.Model, List[models.Model], Dict, List[Dict], None
        ] = None,
        return_response=False,
        **kwargs
    ) -> Union[Dict, List, Response]:
        if model_obj is None:
            return self.endpoint.post()
        if isinstance(model_obj, Dict) or (
            model_obj and isinstance(model_obj, List) and isinstance(model_obj[0], Dict)
        ):
            res = self.endpoint.post(
                data=model_obj,
                clear_unused=False,
                return_response=return_response,
                **kwargs
            )
        elif isinstance(model_obj, list):
            data = [
                mo.to_dict(include_nested=False, only_modified=True) for mo in model_obj
            ]
            res = self.endpoint.post(
                data=data, return_response=return_response, **kwargs
            )
        else:
            data = model_obj.to_dict(include_nested=False, only_modified=True)
            res = self.endpoint.post(
                data=data, return_response=return_response, **kwargs
            )
        return res

    def post(
        self,
        model_obj: Union[
            models.Model, List[models.Model], Dict, List[Dict], None
        ] = None,
        return_response=False,
        **kwargs
    ) -> Union[Dict, List, Response]:
        return self.insert(model_obj, return_response=return_response, **kwargs)

    @suppress_errors
    def delete(
        self,
        identifier: str = None,
        model_obj: Union[models.Model, Dict] = None,
        return_response=False,
        **kwargs
    ) -> Union[Dict, List, Response]:
        if not model_obj:
            kwargs["identifier"] = identifier
        elif isinstance(model_obj, Dict):
            kwargs["data"] = model_obj
            kwargs["identifier"] = identifier or model_obj.pop("id", None)
        elif (
            isinstance(model_obj, list) and model_obj and isinstance(model_obj[0], Dict)
        ):
            kwargs["data"] = model_obj
            kwargs["identifier"] = None
        else:
            # race_condition_check is only supported on certain endpoints
            # if specified on unsupported endpoint will be ignored
            kwargs["data"] = model_obj.to_dict(include_nested=False, only_modified=True)
            kwargs["identifier"] = identifier or model_obj.id
        res = self.endpoint.delete(return_response=return_response, **kwargs)
        return res


class DictController:
    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint

    def get(self, **kwargs) -> List[Dict]:
        return self.endpoint.get(**kwargs)

    def query(self, **kwargs) -> List[Dict]:
        return self.get(**kwargs)

    def post(
        self, model_obj: Dict, return_response=False, **kwargs
    ) -> Union[Dict, List, Response]:
        return self.endpoint.post(model_obj, return_response=return_response, **kwargs)
