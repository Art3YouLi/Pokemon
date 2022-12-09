def get_context():
    if QrContext.instance is None:
        QrContext.instance = QrContext()
    return QrContext.instance


class QrContext():
    instance = None
    all_obj = {}

    def get(self, key):
        return self.all_obj.get(key)

    def add(self, key, v):
        self.all_obj.update({key: v})

    def remove(self, key):
        del self.all_obj[key]
