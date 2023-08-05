Basic Usage 
```Robot
*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported SeleniumLibrary.
Library           SeleniumLibrary
Library           Collections
Library           OperatingSystem
Library           ZapRobotHelper

*** Variables ***
${URL}            https://www.imdb.com/
${browser}        Chrome
${DELAY}          3
${proxy}          selenium-router:9090

*** Keywords ***
Open Browser To IMDB
    ${proxy dict}=   Create Dictionary   proxyType   MANUAL   httpProxy   ${proxy}  ftpProxy    ${proxy}    sslProxy  ${proxy}
    ${default caps}=    Evaluate    sys.modules["selenium.webdriver"].DesiredCapabilities.FIREFOX    sys,selenium.webdriver
    Set To Dictionary    ${default caps}    proxy    ${proxy dict}
    Open Browser    ${URL}    FIREFOX    remote_url=http://selenium-router:4444
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    zap test

Search Movie
    [Arguments]    ${movie}
    Input Text    id=suggestion-search    ${movie}
    Click Button  id=suggestion-search-button
    Page Should Contain  Results for "${movie}"
```
 >File will be downloaded on **'C://projects//HYDRA//reports//zap.html'**
For building wrapper write this command 

This will build all the necessary packages that Python will require.

Also it will create a source distribution

>  python -m build
> 
>  python -m twine upload --repository pypi dist/*
