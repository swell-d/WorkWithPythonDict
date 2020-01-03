# WorkWithPythonDict
Load data from xls, xlsx, xlsm (excel) and csv to python dictionary

Save python dictionary to xlsx (excel) and csv

### Example - Searching for differences in two files and save results to new files

```
from LoadDictFromFile import LoadDictFromFile
from SaveDictToFile import SaveDictToFile

if __name__ == '__main__':
    old_data = LoadDictFromFile.load(filename='old.xlsx', maincolumn='name')
    new_data = LoadDictFromFile.load(filename='new.xlsx', maincolumn='name')

    lost = {}
    same = {}
    new = {}

    for each in old_data.values():
        name = each['name']
        if name not in new_data:
            lost[name] = each

    for each in new_data.values():
        name = each['name']
        if name in old_data:
            same[name] = each
        else:
            new[name] = each

    SaveDictToFile.save_to_xlsx(data=lost, filename='lost')
    SaveDictToFile.save_to_xlsx(data=same, filename='same')
    SaveDictToFile.save_to_xlsx(data=new, filename='new')
```
