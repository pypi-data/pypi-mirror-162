# Install 

```
pip3 install ccstorage --upgrade --user
```

# CCIO: Simple local file read/write

```
content_str = CCIO.read_string(__absolute_path__)
CCIO.save_string(content_str, __absolute_path__)
```

# CCStorage: Local key-value storage

Concat `__root_dir_path__` with `__relative_file_path__` to storage key value.  
When inited, storage will automatically read.  
Then change keys and values, call `write()` to save to file.  

```
storage = CCStorage(__root_dir_path__, __relative_file_path__)  
storage['pending_work'] = True
storage['work_id'] = '123456'
storage.write()

storage = CCStorage(__root_dir_path__, __relative_file_path__)  
print(storage['pending_work'], storage['work_id'])
```

To enable read/write at each value get/set, set `force_reload_at_data_access` to `True`:  

```
storage.force_reload_at_data_access = True
```