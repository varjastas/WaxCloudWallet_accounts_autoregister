from selenium.webdriver.chrome.options import Options
from zipfile import ZipFile
from fake_useragent import UserAgent
from selenium.webdriver import Chrome
from selenium_stealth import stealth
from time import sleep
from datetime import datetime
import os
ua = UserAgent()
def set_options(use_proxy = True, PROXY_HOST = None, PROXY_PORT=None, PROXY_USER = None, PROXY_PASS = None, path_to_captcha = None):
    options = Options()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

        with ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
    
    options.add_argument("start-maximized")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    if path_to_captcha:
        options.add_extension(path_to_captcha)
    options.add_argument('lang=en-US.UTF-8')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return options

def create_browser(path_to_browser, options, console):
    options.arguments[-1]=f"user-agent={get_ua()}"
    console.info(options.arguments)

    browser = Chrome(executable_path=path_to_browser, options=options)
    stealth(browser,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    return browser

def get_ua():
    return ua.chrome

def sleep_before_reg(end, console):
    if int(datetime.now().strftime('%M')) % 10 in [end,(end+1)%10,(end+2)%10]:
        console.info(f'Не сплю, время смены')
        pass
    else:
        if int(datetime.now().strftime('%M'))%10 < end:
            sleep_time = (end-int(datetime.now().strftime('%M'))%10)*60+40
        else:
            sleep_time = ((10+end)-int(datetime.now().strftime('%M'))%10)*60+40
        console.info(f'Сплю {sleep_time} сек')
        sleep(sleep_time)
        return

def new_browser(config, console, options):
    browser = create_browser(config.get('PATH', 'chrome'), options, console)
    sleep(1)
    #Собираем ip и user-agent браузера для сверки, что они не с основы

    browser.get('https://api.ipify.org/')
    sleep(5)
    ip_address = browser.find_element_by_tag_name("body").text
    print(datetime.now())
    console.info(f'browser user-agent: {browser.execute_script("return navigator.userAgent")} ip: {ip_address}')
    return browser

def handler_of_functions(func, *args):
    g = func(args)   
    if g[0] == True:
        pass
    elif g == 'fail':
        try:
            browser.close()
            browser.quit()
        except:
            try:
                os.system('taskkill /im chrome.exe /f')
            except:
                pass
        return 'continue'
    elif g == 'retry':
        sc = 0
        while sc < 3:
            g = func(args)
            if g[0] == True or g == 'fail':
                break
            sc+=1
        if g[0] != True:
            try:
                browser.close()
                browser.quit()
            except:
                try:
                    os.system('taskkill /im chrome.exe /f')
                except:
                    pass
            return 'continue'
    return g

def get_link_with_costil(url, browser, console):
    try:
        browser.get(url)
    except:
        console.error('хуйня с браузером')
        console.exception('')
        try:
            browser.quit()
        except:
            try:
                console.critical('не получилось закрыть браузер')
                browser.quit()
            except:
                console.critical('закрываю через ось, опасна сучка')
                os.system('taskkill /im chrome.exe /f')
        return 'fail'
    return True