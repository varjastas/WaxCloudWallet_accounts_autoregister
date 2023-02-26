''' todo: 
Не приоритет: доделать юзер-агент, чтобы версию хрома нормальную показывало, походу из-за юзер агента мод 2 идет
?: Стоит ли в анкамон функцию коннект к имейлу каждый раз засовывать при чеке сообщений, либо один раз в мейн функцию
Чек на многопотоке, драйвер походу передавать локально, вопрос мультитрединга
'''
from hashlib import new
import logging
from operator import ge
from webbrowser import get



console = logging.getLogger('logger')
handler = logging.FileHandler('output.log', 'w',
                              encoding = 'utf-8')
formatter = logging.Formatter("[%(levelname)s] - %(asctime)s - %(name)s - %(message)s in line %(lineno)d")
handler.setFormatter(formatter)
logging.basicConfig(filename='logging.log', level=logging.INFO)

console.addHandler(handler)

try:
    from modules_selenium import *
    import uncommon_functions as uf
    from time import sleep
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    from  selenium.common.exceptions import WebDriverException
    import pyotp
    from random import randrange
    import os
    from configparser import ConfigParser
except Exception as err:
    console.exception('exception')
    input('stop')
finally:
    console.info('Модули импортированы успешно')

config = ConfigParser()
config.read('./resources/conf.ini')
#Создаем переменные options and useragent
delay = 20 # seconds
accounts = []

with open('./resources/facebook.txt', 'r') as f:
    facebooks = f.read().split('\n')

with open('./resources/outlook.txt', 'r') as f:
    outlooks = f.read().split('\n')

user_agent = get_ua()
print(config.get('PROXY', 'host'))
options = set_options(PROXY_HOST = config.get('PROXY', 'host'), PROXY_PORT = int(config.get('PROXY','port')), PROXY_USER = config.get('PROXY','login'),PROXY_PASS = config.get('PROXY','password'), path_to_captcha=config.get('PATH', 'captcha'))
options.add_argument(f"user-agent={user_agent}")

print(options.arguments)


def fb_login(browser, facebook_login=None, facebook_password=None, facode = None, fb_coc = None):
    try:        
        console.info('загружаю фб')
        #загружаю фб
        if get_link_with_costil('https://www.facebook.com/', browser, console) == 'fail':
            return 'fail'
        sleep(15)

        #ищу подтверждение куки
        try:
            element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[6]/div[1]/div/div[2]/div[4]/button[2]')))
            element.click()
            
            sleep(2)
        except:
            console.info('не нашел куки')
        

        if fb_coc:
            console.info('захожу по кукам')
            for i in fb_coc.split(';'):
                browser.add_cookie({"name":i.split('=')[0], "value":i.split('=')[1]})
            browser.refresh()

            sleep(10)
        else:
            pass
            #Ввожу логин пароль, кликаю некст
            # element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'm_login_email')))
            # element.send_keys(facebook_login)

            # element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'm_login_password')))
            # element.send_keys(facebook_password)

            # element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'login_password_step_element')))
            # element.click()

            # if facode == '2fa':
            #     #ввод 2фа
            #     pass
            # else:
            #     pass
            #проверка входа  
        console.info('проверяю вход')
        try:
            element = WebDriverWait(browser, 25).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div/div[2]/div/article')))
            console.info('мод 1')
            try:
                element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[4]/div/div[1]/div/div/form/div/div/h1'))).text
                if element == 'Your account has been disabled':
                    console.info('акк фб в бане нах')
                    return 'fail'
            except:
                return True, 1
        except:
            try:
                console.info('другой мод')
                element = WebDriverWait(browser, 25).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[1]/table/tbody/tr/td[2]/div/div[1]')))
                console.info('mode2')
                return True, 2
            except:
                console.critical('чето необычное, смари лог')
        return True, 1

    except TimeoutException:
        console.exception('')
        return 'retry'

    except WebDriverException as Err:
        message = Err.__str__
        if 'ERR_PROXY_CONNECTION_FAILED' in str(message):
            console.warning('прокси хуево')
            sleep(20)
            return 'retry'
        else:
            console.exception('')
            console.error('Хуйня с фб')
            return 'fail'

    except Exception as Err:
        console.info('some error, skipping acc', Err)
        return 'fail'

def waxreg(browser, outlook_login, outlook_password, mail, mode = 1):
    try:
        #Загружаю вакс
        console.info('загружаю вакс')
        if get_link_with_costil('https://wallet.wax.io/dashboard', browser, console) == 'fail':
            return 'fail'

        console.info('Кликаю на фб')
        #Кликаю на фб
        element = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div/div[3]/div[1]/div[1]/button')))
        sleep(15)
        browser.execute_script('document.querySelector("#facebook-social-btn").click()')
        console.info('кликнул')
        sleep(15)
        
        #Закрываю доступ почты и жму некст
        if 'all-access.wax.io' in browser.current_url:
            sleep(15)

        if 'steam' in browser.current_url:
            pass
        else:
            if mode == 1:
                element = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[3]/div/div[1]/form/div/div/div[1]/div/section[2]/div[1]/div/div/div[2]/div/div/a')))
                element.click()    
                sleep(1)                                                                     
                element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[3]/div/div[1]/form/div/div[2]/div[1]/div/section[1]/div/div/div/fieldset/label[2]/div/div[2]/div/span')))
                element.click()
                try:
                    element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[3]/div/div[1]/form/div/div[2]/div[2]/div[1]/footer/div/div[1]/button')))
                    element.click()
                except:
                    element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[3]/div/div[1]/form/div/div[2]/div[2]/div[1]/footer/div/div/div[2]/button')))
                    element.click()
                    
            elif mode == 2:
                element = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/form/div[1]/div[2]/div/div[1]/div[2]/a')))
                element.click()    
                sleep(1)                                                                     
                element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[1]/form/div[1]/div[2]/div[2]/fieldset/label[2]/table/tbody/tr/td[2]/div/input')))
                element.click()
                try:
                    element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/form/div[2]/table/tbody/tr/td[2]/input[1]')))
                    element.click()
                except:
                    try:
                        element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[1]/form/div[2]/table/tbody/tr/td[2]/input')))
                        element.click()
                    except:
                        pass
        sleep(15)
        if 'steam' in browser.current_url:
            pass
        else:
            element = WebDriverWait(browser, 45).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div/div[3]/div[1]/div[1]/button')))
            element.click()
        
        #Ввод своей почты
        console.info('ввожу почту')


        element = WebDriverWait(browser, 45).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/section/div[2]/div/form/div[1]/div/input')))
        element.send_keys(outlook_login)

        sleep(1)
        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/section/div[2]/div/form/div[3]/button')))
        element.click()

        console.info('Жду письмо от вакса')
        #Заход по imap в почту
        sleep(10)

        
        src = uf.parse(mail, mode = 1)
        if src =='retry':
            return 'retry'
        console.info(src)

        if get_link_with_costil(src, browser, console) == 'fail':
            return 'fail'

        console.info('Кликаю галочки')

        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/section/form/label[1]/span[1]/span[1]/input')))
        element.click()

        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/section/form/label[2]/span[1]/span[1]/input')))
        element.click()

        sleep(2)
        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/section/form/div/button')))
        element.click()
        sleep(30)

        return True

    except TimeoutException:
        console.info('Timeout Exception, restarting')
        return 'retry'

    except WebDriverException as Err:
        message = Err.__str__
        if 'ERR_PROXY_CONNECTION_FAILED' in str(message):
            console.info('прокси хуево')
            sleep(20)
            return 'retry'
        else:
            console.exception('')
            return 'fail'


    except Exception as Err:
        console.info('some error, skipping acc', Err)
        return 'fail'

def set2fa(mail, browser):
    try:
        console.info('гружу страницу 2фа')
        if get_link_with_costil('https://all-access.wax.io/account/security', browser, console) == 'fail':
            return 'fail'

        sleep(5)

        #энейбл 2фа
        element = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[1]/span/div/button')))
        element.click()
        
        sleep(7)
        code = uf.parse(mail, mode=2)
        if isinstance(code, str):
            if code == 'retry':
                return 'retry'
        console.info(code)

        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/div[2]/form/div/div/div/input')))
        element.send_keys(code)
        
        sleep(2)
        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/div[2]/form/span/div/button')))
        element.click()
        
        sleep(3)
        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/div[1]/div[3]/h6')))
        code_2_fa = element.text.replace(' ', '')
        console.info(f'2fa code is {code_2_fa}')

        totp = pyotp.TOTP(code_2_fa)
        code_to_verify = totp.now()
        console.info(f'now {code_to_verify}')

        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/div[2]/form/div/div/div/input')))
        element.send_keys(code_to_verify)
        sleep(2)
        
        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/div[2]/form/span/div/button')))
        element.click()
        try:
            element = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/span[3]')))
            restore_2fa = element.text
        except:
            try:
                sleep(30)
                element = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/span[3]')))
                restore_2fa = element.text
            except:
                restore_2fa = 'соряннепрогрузило'
        #exit from account
        console.info(f'code to restore: {restore_2fa}')
        element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[1]/nav/a[5]')))
        element.click()
        sleep(15)

        return code_2_fa, restore_2fa

    except TimeoutException:
        console.info('Timeout Exception, restarting')
        return 'retry'

    except WebDriverException as Err:
        message = Err.__str__
        if 'ERR_PROXY_CONNECTION_FAILED' in str(message):
            console.info('yes')
            sleep(20)
            return 'retry'
        else:
            console.info(Err)
            return 'fail'

    except Exception as Err:
        console.info('some error, skipping acc', Err)
        return 'fail'

def forgot_password(mail, outlook_login, browser):
    try:
        
        console.info('Сбрасываю пароль')
        
        if get_link_with_costil('https://all-access.wax.io/forgot-password', browser, console) == 'fail':
            return 'fail'
        sleep(5)

        #Enter email
        sc = 0
        cos = False
        while sc < 3:
            element = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/div/form/div/div[1]/div/div/input')))
            sleep(5)  
            element.send_keys(outlook_login)
            if uf.solve_captcha('/html/body/div[1]/div/section/div[2]/div/form/div/div[2]/div[2]/div/div/div/button', browser):
                cos = True
                break
            else:
                sc += 1
                browser.refresh()
                sleep(10)
        if not cos:
            return 'fail'
        console.info('Жду ссылку')

        sleep(8)
        src = uf.parse(mail, mode=3)
        if src == 'retry':
            return 'retry'
        
        console.info(f'Ссылка: {src} , загружаю смену пароля')
        if get_link_with_costil(src, browser, console) == 'fail':
            return 'fail'

        password_wax = uf.gen_password(randrange(4,5))
        console.info(f'Wax password is {password_wax}')

        #enter password and solve captcha
        console.info('Меняю пароль')

        sc = 0
        cos = False
        sleep(20)
        while sc < 3:
            element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/div/form/div/div[1]/div[1]/div/input')))
            sleep(5) 
            element.send_keys(password_wax)
            if uf.solve_captcha('/html/body/div[1]/div/section/div[2]/div/form/div/div[2]/div[2]/div/div/div/button', browser):
                sleep(5)
                cos = True
                break
            else:
                sc += 1
                browser.refresh()
                sleep(10)
        if not cos:
            return 'fail'
        sleep(15)
        return password_wax

    except TimeoutException:
        console.info('Timeout Exception, restarting')
        return 'retry'

    except WebDriverException as Err:
        message = Err.__str__
        if 'ERR_PROXY_CONNECTION_FAILED' in str(message):
            console.info('прокси хуево')
            sleep(20)
            return 'retry'
        else:
            console.exception(Err)
            return 'fail'

    except Exception as Err:
        console.exception('some error, skipping acc')
        return 'fail'

def main(fa_fb = False, fb_coc = False):
    while facebooks:
        # sleep_before_reg(7, console)
        try:
            outlook = outlooks.pop()
            outlook_login = outlook.split(':')[0]
            outlook_password = outlook.split(':')[1]
            mail = uf.connect_by_imap(outlook_login, outlook_password)
        except:
            console.warn('Не зашло в почту((((((')
            continue
        try:
            browser = new_browser(config, console, options)
        except Exception as Err:
            try:
                browser.close()
                browser.quit()
            except:
                outlooks.append(outlook)
                try:
                    os.system('taskkill /im chrome.exe /f')
                except:
                    pass
            console.info('Не получается создать браузер, последний фб:', facebooks[-1])
            console.exception(Err)
            sleep(30)
            continue
        try:
            
            temp_list = []

            facebook = facebooks.pop()
            facebook_login = facebook.split(':')[0]
            facebook_password = facebook.split(':')[1]
            facebook_2fa = None
            cookie = None
            if fa_fb:
                facebook_2fa = facebook.split(':')[2]
            if fb_coc:
                cookie = 'c_user' + facebook.split(':c_user')[1]

            console.info(f'outlook login: {outlook_login} outlook password: {outlook_password}\nfacebook login: {facebook_login} facebook password: {facebook_password}')

            handler_of_functions(fb_login, )

            g = waxreg(outlook_login, outlook_password, mail, mode = g[1])
            if g == True:
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
                continue
            elif g == 'retry':
                sc = 0
                while sc < 3:
                    g = waxreg(outlook_login, outlook_password, mail)
                    if g != 'retry':
                        break
                    sc+=1
                if g != True:
                    try:
                        browser.close()
                        browser.quit()
                    except:
                        try:
                           os.system('taskkill /im chrome.exe /f')
                        except:
                            pass 
                    continue

            g = set2fa(mail)
            if isinstance(g, tuple):
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
                continue
            elif g == 'retry':
                sc = 0
                while sc < 3:
                    g = set2fa(mail)
                    if isinstance(g, tuple):
                        break
                    elif isinstance(g, str):
                        if g == 'fail':
                            break
                    sc+=1
                if not isinstance(g, tuple):
                    try:
                        browser.close()
                        browser.quit()
                    except:
                        try:
                            os.system('taskkill /im chrome.exe /f')
                        except:
                            pass
                    continue

            temp_list.append(g[0])
            temp_list.append(g[1])

            g = forgot_password(mail, outlook_login)
            if g != 'fail' and g != 'retry':
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
                continue
            elif g == 'retry':
                sc = 0
                while sc < 3:
                    g = forgot_password(mail, outlook_login)
                    if g != 'retry':
                        break
                    sc+=1
                if g == 'fail' or g == 'retry':
                    try:
                        browser.close()
                        browser.quit()
                    except:
                        try:
                            os.system('taskkill /im chrome.exe /f')
                        except:
                            pass
                    continue


            temp_list.append(g)

            #Записывает втф бат без новой строки
            temp = outlook_login+':'+temp_list[2]+':'+temp_list[0]+':'+temp_list[1]+'\n'
            accounts.append(temp)
            with open('accounts.txt', 'a') as f:
                f.write(temp)

            browser.close()
            browser.quit()

        except TimeoutException:
            console.info('timeout exception')
            try:
                browser.close()
                browser.quit()
            except:
                try:
                    os.system('taskkill /im chrome.exe /f')
                except:
                    pass
            continue

        except Exception as Err:
            console.exception('some error')
            try:
                browser.close()
                browser.quit()
            except:
                try:
                    os.system('taskkill /im chrome.exe /f')
                except:
                    pass
    console.info(accounts)

if __name__ == '__main__':
    main(fa_fb=True, fb_coc=True)