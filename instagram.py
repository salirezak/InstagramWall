from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import requests

XPATHS = {
    "Not Now" : "//button[contains(text(), 'Not Now')]|//a[contains(text(), 'Not Now')]",
    "Options" : '//*[name()="svg"][@aria-label="Options"]',
    "Log Out_div" : "//div[contains(text(), 'Log Out')]",
    "Log Out_button" : "//button[contains(text(), 'Log Out')]",
    "Accept All" : "//button[contains(text(), 'Accept All')]",
    "alert" : '//*[@role="alert"]',
    'Home' : '//*[name()="svg"][@aria-label="Home"]',
    'Instagram' : "//h1[contains(text(), 'Instagram')]"
}
USERAGENT = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
HOST = 'https://www.instagram.com/'



class Routing:
    def __init__(self, inpage):
        self.inpage = inpage

    def __call__(self, driver):
        if driver.find_elements(By.XPATH, XPATHS['Accept All']): return 'acceptcookies'

        if errors := driver.find_elements(By.XPATH, XPATHS['alert']):
            return list(map(lambda err: err.text, errors))

        if self.inpage == 'login':
            if driver.find_elements(By.XPATH, XPATHS['Not Now']): return 'saveinfo'
            if driver.find_elements(By.NAME, "verificationCode"): return 'verify'

            if driver.find_elements(By.XPATH, XPATHS['Home']): return True

        if self.inpage == 'verify':
            if driver.find_elements(By.XPATH, XPATHS['Not Now']): return 'saveinfo'

            if driver.find_elements(By.XPATH, XPATHS['Home']): return True

        if self.inpage == 'saveinfo':
            if driver.find_elements(By.XPATH, XPATHS['Home']): return True

        if self.inpage == 'logout':
            if driver.find_elements(By.XPATH, XPATHS['Instagram']): return True

        return False


class InstagramLoginouter:
    def __init__(self, wait_time=20, driver_path=r'bin/geckodriver', cookie=None, useragent=USERAGENT):
        self.USERAGENT = useragent
        self.HOST = HOST
        self.driver= self.__driver__(driver_path)
        self.wait = WebDriverWait(self.driver, wait_time)
        if cookie: self.__update__(cookie)
        #self.driver.set_page_load_timeout(wait_time)
        #self.driver.implicitly_wait(wait_time)

    def __driver__(self, driver_path):
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.set_preference("general.useragent.override", self.USERAGENT)  ## Set useragent
        options.set_preference('devtools.jsonview.enabled', False)  ## Turns json viewer off
        options.set_preference('network.captive-portal-service.enabled', False)
        options.set_preference('permissions.default.image', 2) ## Disable images

        service = Service(driver_path)
        return Firefox(service=service, options=options)

    def __update__(self, cookies):
        self.driver.get(self.HOST)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()

    def __del__(self):
        self.driver.quit()

    def __acceptcookies__(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS['Accept All'])), message='no "Accept All" button').click()
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, XPATHS['Accept All'])), message='no "Accept All" button')

    def __saveinfo__(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS['Not Now'])), message='no "Not Now" button').click()

        result = self.wait.until(Routing('saveinfo'), message='unexpected error in "Don\'t Saving Info"')

        if result == 'acceptcookies':
            self.__acceptcookies__()
            result = self.wait.until(Routing('saveinfo'), message='unexpected error in "Don\'nt Saving Info"')

        return result

    def login(self, username, password):
        self.driver.get(self.HOST + 'accounts/login/')

        username_elem = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')), message='no "username" input')
        username_elem.clear()
        username_elem.send_keys(username)

        password_elem = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')), message='no "password" input')
        password_elem.clear()
        password_elem.send_keys(password)
        password_elem.send_keys(Keys.ENTER)

        result = self.wait.until(Routing('login'), message='unexpected error in "Logging In"')

        if result == 'acceptcookies':
            self.__acceptcookies__()
            result = self.wait.until(Routing('login'), message='unexpected error in "Logging In"')

        if result == 'saveinfo':
            return self.__saveinfo__()

        return result

    def verify(self, verification):
        verificationcode_elem = self.wait.until(EC.presence_of_element_located((By.NAME, 'verificationCode')), message='no "verificationCode" input')
        verificationcode_elem.clear()
        verificationcode_elem.send_keys(verification)
        verificationcode_elem.send_keys(Keys.ENTER)

        result = self.wait.until(Routing('verify'), message='unexpected error in "Verifying"')

        if result == 'acceptcookies':
            self.__acceptcookies__()
            result = self.wait.until(Routing('verify'), message='unexpected error in "Verifying"')

        if result == 'saveinfo':
            return self.__saveinfo__()

        return result

    def logout(self, username):
        self.driver.get(self.HOST + f'{username}/')

        self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS['Options'])), message='no "Options" svg').click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS['Log Out_div'])),message='no "Log Out" div').click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS['Log Out_button'])),message='no "Log Out" button').click()

        result = self.wait.until(Routing('logout'), message='unexpected error in "Logging Out"')

        if result == 'acceptcookies':
            self.__acceptcookies__()
            result = self.wait.until(Routing('logout'), message='unexpected error in "Logging Out"')

        return result

    def cookie(self):
        return self.driver.get_cookies()

    def screen(self):
        return self.driver.get_screenshot_as_base64()


def Checker(in_cookies):
    cookies = {cookie['name']:cookie['value'] for cookie in in_cookies} if in_cookies else {}
    response = requests.get(url=HOST + 'data/shared_data/', cookies=cookies)

    try:
        js = response.json() if response.json() else None
        config = js.get('config') if js else None
        viewer = config.get('viewer') if config else None

        country_code = js.get('country_code') if js else None
        viewerId = config.get('viewerId') if config else None
        username = viewer.get('username') if viewer else None

        return response, {'country':country_code, 'userid':viewerId, 'username':username}

    except requests.exceptions.JSONDecodeError:
        return response, {'country':None, 'userid':None, 'username':None}


def StoryUploader(in_cookies, pic):
    cookies = {cookie['name']:cookie['value'] for cookie in in_cookies}
    upload_id = int(datetime.now().timestamp())
    data = {'upload_id': upload_id, 'caption': ''}

    headers = {
        'Content-Length'  : str(len(pic)),
        'X-Entity-Length' : str(len(pic)),
        'X-Entity-Name'   : f'fb_uploader_{upload_id}',
        'X-Instagram-Rupload-Params': '{"media_type":1,"upload_id":"%s","upload_media_height":700,"upload_media_width":400}' % upload_id,
        'Offset'          : '0',
        'X-Entity-Type'   : 'image/jpeg',
        'Content-Type'    : 'image/jpeg',
        'Accept'          : '*/*',
        'Sec-Fetch-Mode'  : 'cors',
        'Sec-Fetch-Dest'  : 'empty',
        'Sec-Fetch-Site'  : 'same-site',
        'Referer'         : 'https://www.instagram.com/',
    }
    url = HOST + f'rupload_igphoto/fb_uploader_{upload_id}'
    response = requests.post(url, headers=headers, data=pic, cookies=cookies)

    if not ((js := response.json()) and (status := js.get('status')) and status == 'ok'):
        return response, None

    headers = {
        'Content-Length'   : '32',
        'X-Requested-With' : 'XMLHttpRequest',
        #'X-Ig-Www-Claim'   : response.headers['X-Ig-Set-Www-Claim'],
        'X-Csrftoken'      : cookies['csrftoken'],
        'Content-Type'     : 'application/x-www-form-urlencoded',
        'Accept'           : '*/*',
        'Sec-Fetch-Mode'   : 'cors',
        'Sec-Fetch-Dest'   : 'empty',
        'Sec-Fetch-Site'   : 'same-origin',
        'Referer'          : 'https://www.instagram.com/create/story/',
    }
    url =  HOST + 'create/configure_to_story/'
    response = requests.post(url, headers=headers, data=data, cookies=cookies)

    if not ((js := response.json()) and (media := js.get('media')) and \
            (user := media.get('user')) and \
            (username := user.get('username')) and (pk := media.get('pk'))):
        return response, None

    return response, HOST + f'stories/{username}/{pk}/'