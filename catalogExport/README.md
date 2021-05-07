# Export catalog
This is a Python script in order to export your GoodBarber catalog for Google Merchants and Facebook

## Export products for Facebook and Google
If you need to add some specific fields in GoogleMerchant or Facebook, you need to modify the code
inside. The script generate a tsv format file compatible in both case.

## Create your config file
Take the config_example.py file in order to set up your own configuration: public_api/config

## Installation

Create a virtual environment with:

```bash
python3 -m venv [FOLDER_NAME]
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all the requirements.

```bash
pip install requirements.txt
```

Type this command to begin the export

```bash
python3 export_catalog -f <name_of_file>
```


## License
[MIT]%