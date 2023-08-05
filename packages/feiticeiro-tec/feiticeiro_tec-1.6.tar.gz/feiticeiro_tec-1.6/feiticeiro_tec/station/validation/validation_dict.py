from contextlib import suppress
class ValidationDict():
    def __init__(self,data,default=None):
        self._data = dict(data)
        self.default = default

    def __getitem__(self,valor):
        return self._data[valor]

    def get(self,key,Type=None):
        """Recebe uma key e com conversor."""
        response = self._data[key]
        if Type:
            with suppress(Exception):
                return Type(response)
            return self.default
        return response

    def __repr__(self) -> str:
        return f'<ValidationDict {list(self._data.keys())}>'