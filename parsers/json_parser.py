class JSONParser:
    def __init__(self, items_root: str, item_key: str, title_key: str):
        self.items_root = items_root
        self.item_key = item_key
        self.title_key = title_key

    def parse(self, response: dict):
        items_root: dict = response[self.items_root]
        items = self._parse(self.item_key)
        return items

    def _parse(self, keys: list, response: dict):
        if hasattr(response, 'iteritems'):
            for k, v in response.iteritems():
                for key in keys:
                    if k == key:
                        yield k, v
                    if isinstance(v, dict):
                        for result in self._parse(key, v):
                            yield result
                    elif isinstance(v, list):
                        for d in v:
                            for result in self._parse(key, d):
                                yield result
