import json

class JsonCustomEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.number, np.ndarray)):
            return obj.tolist()
        elif isinstance(obj, complex):
            return [obj.real, obj.imag]
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, bytes):
            return obj.decode()
        return json.JSONEncoder.default(self, obj)

