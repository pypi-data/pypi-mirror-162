import os
import json
from typing import Union


class CCIO:

    @staticmethod
    def read_string(file_name):
        if os.path.isfile(file_name):
            with open(file_name) as f:
                lst = f.read()
                return lst
        else:
            return None

    @staticmethod
    def save_string(string, file_name):
        dir_path = os.path.dirname(file_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(file_name, "w") as f:
            f.write(string)


class CCStorage:

    def __init__(self, root_dir_path: str, relative_file_path: str):
        self.__abs_path: str = os.path.realpath(os.path.join(root_dir_path, relative_file_path))
        self.__storage_dict: {str: str} = {}
        self.force_reload_at_data_access = False  # 每次存取字段时都要强制读写持久化文件，daemon中重启进程的storage建议开启
        self.read()

    def write(self) -> None:
        json_str = json.dumps(self.__storage_dict, indent=4, ensure_ascii=False)
        CCIO.save_string(json_str, self.__abs_path)

    def read(self) -> bool:
        content = CCIO.read_string(self.__abs_path)
        if content is not None and isinstance(content, str):
            try:
                result = json.loads(content)
                if isinstance(result, dict):
                    self.__storage_dict = result
                    return True
            except Exception as e:
                print('ccstorage read exception: ', e)
        return False

    def __setitem__(self, key: str, value: Union[str, float, dict, list, None]) -> None:
        if self.force_reload_at_data_access is True:
            self.read()
        if value is None:
            self.__storage_dict.pop(key, None)
        else:
            self.__storage_dict[key] = value
        if self.force_reload_at_data_access:
            self.write()

    def __getitem__(self, item) -> Union[str, float, dict, list]:
        if self.force_reload_at_data_access:
            self.read()
        return self.__storage_dict.get(item)

    def get(self, key):
        return self.__storage_dict.get(key)

    def keys(self):
        return self.__storage_dict.keys()
