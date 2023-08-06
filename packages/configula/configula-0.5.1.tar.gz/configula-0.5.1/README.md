# Configula

Creates a single configuration by merging settings defined in:
    1. in environment variables
    2. in toml file

Values provided in **environment variables have priority** over values from 
toml configuration file.

By default all environment variables are prefixed with 'PAPERMERGE'.
By default `__` (two underscores) is used as delimiter in environment variables
names. For example, given following toml file:

    [main]
    secret_key = 1234
    [ocr]
    default_language = 'deu'

corespondent environment variables names are PAPERMERGE__MAIN__SECRET_KEY and
PAPERMERGE__OCR__DEFAULT_LANGUAGE - notice two underscores separate section name
from prefix and variable name.
Environment variable name format is (all in uppercase):

     <prefix><delimiter><section_name><delimiter><variable_name>


Although in toml files you can place variable names outside sections, in Papermerge
all variables **must be placed in sections**.

By default Configula looks up for following toml file:

- /etc/papermerge/papermerge.toml
- /etc/papermerge.toml
- papermerge.toml

If you have custom location (or custom file name), use ``PAPERMERGE__CONFIG``
(notice double underscores) environment variable to point to it:

    PAPERMERGE__CONFIG=/app/config/pm.toml


## Installation

    $ poetry add configula

## Usage

    from configula import Configula
 
    config = Configula()
    
    default_language = config.get('ocr', 'default_language')
    secret_key = config.get('main', 'secret_key')

Where ``papermerge.toml`` has the following content:

    [main]
    secret_key = 5432

    [ocr]
    default_language = 'deu'

Default language can be overwritten by environment
variable `PAPERMERGE__OCR__DEFAULT_LANGUAGE` and secret_key can overwritten
by environment variable `PAPERMERGE__MAIN__SECRET_KEY`

If you want to read variable from a section use
`configula.get(section, var_name, default_value)` method.
