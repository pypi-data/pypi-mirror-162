from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
class Browser:
    Chrome = 'chrome'
    Edge = 'edge'
    Firefox = 'firefox'
def get_options(browser):
    if browser == Browser.Chrome:
        return webdriver.ChromeOptions()
    elif browser == Browser.Edge:
        return webdriver.EdgeOptions()
    elif browser == Browser.Firefox:
        return webdriver.FirefoxOptions()
    else:
        raise TypeError('Browser %s not supported' %(browser))
def init_browser(browser,*args,**kwargs):
    if browser == Browser.Chrome:
        return webdriver.Chrome(*args,**kwargs)
    elif browser == Browser.Edge:
        return webdriver.Edge(*args,**kwargs)
    elif browser == Browser.Firefox:
        return webdriver.Firefox(*args,**kwargs)
    else:
        raise TypeError('Browser %s not supported' %(browser))
def clickx(driver,ele): #Click on the ele(ment) through xpath by ActionChains
    spot=driver.find_element(by=By.XPATH,value=ele)
    ActionChains(driver).click(spot).perform()
def enterx(driver,word,ele): #Put the word(s) in the ele(ment) through xpath
    spot=driver.find_element(by=By.XPATH,value=ele)
    spot.send_keys(Keys.CONTROL,'a') #Select all making sure it's empty
    spot.send_keys(word)