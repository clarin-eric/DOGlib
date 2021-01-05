class JSONParser:
    def __init__(self, items_root: str, title_key: str, item_key: str):
        self.items_root = items_root
        self.title_key = title_key
        self.item_key = item_key

    def parse(self, response: dict):
        items_root: dict = response[self.items_root]
        items = self.gen_dict_extract(self.item_key)
        return items

    def gen_dict_extract(self, key, response: dict):
        if hasattr(response, 'iteritems'):
            for k, v in response.iteritems():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in self.gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.gen_dict_extract(key, d):
                            yield result
