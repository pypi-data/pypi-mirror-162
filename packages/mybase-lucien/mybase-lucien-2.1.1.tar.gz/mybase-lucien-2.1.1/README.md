# Package `mybase-lucien`
This package is used for setting up base locales.

Pay attention, this package does not require the dependency of `selenium` while being installed by pip, but `selenium` is required to be installed if `myselenium` is imported.

To install:
```shell
pip install mybase-lucien
```

To import:
```python
import mybase_lucien
```

## Module `myip`
This deals the problems with ip adresses.
### Import
```python
from mybase_lucien import myip
```
### Function `get()`
It gets current outbound ip address.
- usage
  ```python
  ip = myip.get()
  ```
- arguments  
  There are no arguments.
- returned value  
  A string value, which is the ip address. It would be empty if the program fails to fetch the ip address. 
## Module `mylocale`
This checks the current operating locales.
### Import
```python
from mybase_lucien import mylocale
```
### Function `is_exec()`
This determines whether the currently running program is a script file run by the python interpreter or a packaged application.
- usage
  ```python
  is_executable = mylocale.is_exec()
  ```
- arguments  
  There are no arguments.
- returned value  
  A bool value, indicating if this is a packaged application (True for yes).
### Function `get_dir()`
This fetches the directory the script file or the packaged application is located. 
- usage
  ```python
  mydir = mylocale.get_dir()
  ```
- arguments  
  There are no arguments.
- returned value  
  A string value which is the directory mentioned above.
## Module `myselenium`
This provides easy-to-use multi-browser support based on the package `selenium`.  
Pay attention: `selenium` must be installed first using:
```shell
pip install selenium
```
### Import
```python
from mybase_lucien import myselenium
```
### Function `get_options(browser)`
This returns a browser options object.
- usage
  ```python
  options = myselenium.get_options(browser=myselenium.Browser.Chrome)
  ```
- arguments
  - `browser`  
    A string value which represents certain browser types, which can be choose from:
    ```python
    # Chrome
    myselenium.Browser.Chrome
    # Edge
    myselenium.Browser.Edge
    # Firefox
    myselenium.Browser.Firefox
    ```
- returned value  
  A browser options object.
### Function `init_browser(browser,*args,**kwargs)`
This initiates a driver of the given browser.
- usage
  ```python
  driver = myselenium.init_browser(browser=myselenium.Browser.Chrome,'/path/to/chromedriver',options=options)
  ```
- arguments
  - `browser`  
    A string value which represents certain browser types, which can be choose from:
    ```python
    # Chrome
    myselenium.Browser.Chrome
    # Edge
    myselenium.Browser.Edge
    # Firefox
    myselenium.Browser.Firefox
    ```
  - Other arguments  
    Any argument that can be used when initializing a webdriver.
- returned value  
  A webdriver instance of the given browser.
### Function `clickx(driver,ele)`
This operates the driver to click on the certain element found by xpath.
- usage
  ```python
  clickx(driver,ele)
  ```
- arguments
  - `driver`  
    A webdriver instance.
  - `ele`  
    A string value which is the xpath of a certain element.
- returned value  
  There are no returned values.
### Function `enterx(driver,ele)`
This operates the driver to input words to the certain element found by xpath.
- usage
  ```python
  enterx(driver,ele)
  ```
- arguments
  - `driver`  
    A webdriver instance.
  - `ele`  
    A string value which is the xpath of a certain element.
- returned value  
  There are no returned values.
