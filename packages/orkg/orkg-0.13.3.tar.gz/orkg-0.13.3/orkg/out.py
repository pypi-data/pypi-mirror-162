from typing import Union
import warnings


class OrkgResponse(object):

    @property
    def succeeded(self) -> bool:
        return str(self.status_code)[0] == '2'

    def __init__(self, response, status_code: str, content: Union[list, dict], url: str, paged: bool):
        if response is None and status_code is None and content is None and url is None:
            raise ValueError("either response should be provided or content with status code")
        if not paged:
            warnings.warn("You are running an out-of-date ORKG backend! GET (i.e., listing) calls now provide pagination information", DeprecationWarning)
        if (response is not None and str(response.status_code)[0] != '2') or (status_code is not None and content is not None and status_code[0] != '2'):
            self.status_code = response.status_code if response is not None else status_code
            self.content = response.content if response is not None else content
            self.pageable = None
            return
        if response is not None:
            self.status_code = response.status_code
            self.content = response.json() if len(response.content) > 0 else response.content
            self.pageable = None
            if paged and isinstance(self.content, dict):
                self.pageable = self.content['pageable'] if 'pageable' in self.content else None
                self.content = self.content['content'] if 'content' in self.content else self.content
            self.url = response.url
        if status_code is not None and content is not None:
            self.status_code = status_code
            self.content = content
            self.pageable = None
            if paged and isinstance(self.content, dict) and 'content' in content:
                self.pageable = self.content['pageable'] if 'pageable' in self.content else None
                self.content = self.content['content']
            self.url = url

    def __repr__(self):
        return "%s %s" % ("(Success)" if self.succeeded else "(Fail)", self.content)

    def __str__(self):
        return self.content
