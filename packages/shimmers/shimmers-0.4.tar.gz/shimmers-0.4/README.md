# shimmers

simple client to upload files to / from an office 365 sharepoint site 
using [waddle](https://pypi.org/project/waddle) to provide credential management.
named after the group of hummingbirds.  _pax avium_.

based on [office365-rest-python-client](https://github.com/vgrem/Office365-REST-Python-Client/)

## quick start

```bash
pip install shimmers
```

## usage

### uploading a file

```python
from waddle import load_config
from shimmers import Sharepoint
from io import BytesIO
conf = load_config('path/to/conf.yml')
sharepoint = Sharepoint(conf=conf, site_name='my_site')
buff = new BytesIO()
buff.write('hello, shimmers!\n'.encode('utf-8'))
sharepoint.upload(buff, 'Documents/hello_shimmers.txt')
```

### downloading a file

```python
from waddle import load_config
from shimmers import Sharepoint
conf = load_config('path/to/conf.yml')
sharepoint = Sharepoint(conf=conf, site_name='my_site')
buff = sharepoint.download('Documents/hello_shimmers.txt')
st = buff.getvalue().decode('utf-8')
print(st)
```

### uploading a set of dataframes as a single excel spreadsheet

```python
from waddle import load_config
from pandas import DataFrame
from shimmers import Sharepoint
conf = load_config('path/to/conf.yml')
sharepoint = Sharepoint(conf=conf, site_name='my_site')
df1 = DataFrame([dict(pet='sesame', type='cat'), dict(pet='peanut', type='dog')])
df2 = DataFrame([dict(pet='cody', owner='will'), dict(pet='kho', owner='boris')])
sharepoint.upload_dataframes('Documents/pets.xlsx', df1, 'names', df2, 'owners')
```
