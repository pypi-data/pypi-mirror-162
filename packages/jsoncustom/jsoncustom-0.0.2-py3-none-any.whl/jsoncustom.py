import json


class JsonCustom:
    def __init__(self, path_file):
        self.path_file = path_file

    def function_reed(self):
        return json.load(self.obj)

    def function_write(self):
        return json.dump(self.data, self.obj, indent=4, ensure_ascii=False)


    def with_open(self, w_a, function, encoding="utf-8"):
        with open(self.path_file, f'{w_a}', encoding=encoding) as self.obj:
            return function()

    def reed(self):
        try:
            return self.with_open('r', self.function_reed)
        except:
            return self.with_open('r', self.function_reed, "cp1251")

    def write(self):
        return self.with_open('w', self.function_write)

    def update_json_list(self, list_update):
        self.list = self.reed()
        self.list.extend(list_update)
        self.data = self.list
        self.write()

    def delete_string_json_list(self, list_pop):
        list = self.reed()
        list.pop(list_pop)
        self.data = list
        self.write()

    def update_json_dict(self, dict_update):
        self.json_dict = self.reed()
        self.json_dict.update(dict_update)
        self.data = self.json_dict
        self.write()