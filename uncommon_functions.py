import random
from outlook import Outlook
from selenium.webdriver.common.by import By
from time import sleep

def gen_password(length, name_or_password = False):
    chars = [list('abcdefghijklnopqrstuvwxyz'), list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), list('1234567890')]
    pasw = ''
    random.shuffle(chars)
    for i in chars:
        random.shuffle(i)
        temp = ''.join([random.choice(i) for x in range(length)])
        pasw += temp
    pasw += '$'
    return pasw


def connect_by_imap(login, password):
    mail = Outlook()	
    mail.login(login,password)
    mail.inbox()
    return mail

def get_last_message(mail):
    ids = mail.allIds()
    id_w_word = ids[-1]
    id = str(id_w_word)[2:-1]
    print(id, type(id))
    mail.getEmail(str(id_w_word)[2:-1])
    message = mail.mailbody()
    from_ = mail.mailfrom()
    return [message, from_]

def parse(mail, mode=None):
    count_retries = 0
    if not mode:
        return 'mode not set'
    
    #confirm acc
    while count_retries <= 10:
        message, from_ = get_last_message(mail)
        if from_ == 'WAX All Access <info@wax.io>':
            print('found message from wax')
            try:
                if mode == 1:
                    s = int(message.find('https://api-login.wax.io/v1/register/soc='))
                    f = int(message.find('style=3D"padding-top: =')) - 2 
                    g = int(f)
                    src = str(message)[s:g].replace(' ', '').replace('soc=', 'soc').replace('\r', '').replace('\n', '').replace('token=3D', 'token=')
                    if 'register' in src:
                        return src
                elif mode == 2:
                    s = int(message.find('top: 0">'))
                    code = message[s+8:s+14]
                    int(code)
                    return code
                elif mode == 3:
                    pos1 = message.find('https://all-access.wax.io/forgot-passwor=')
                    pos2 = message.find('" style=3D"padding-top: 0;padding=')
                    src = message[pos1:pos2].replace('passwor=', 'passwor').replace('\r', '').replace('\n', '').replace('token=3D', 'token=')
                    if 'forgot-passwor' in src:
                        return src
                    
                    return src
            except Exception as Err:
                print(Err)

        sleep(6)
        count_retries += 1
    return 'retry'

        
def solve_captcha(xpath_path, browser):
    s = True
    for i in range(10):
        sleep(4)
        try:
            print(f'trying {i} time')
            element = browser.find_element(By.XPATH, xpath_path)
            sleep(2)
            element.click()
            s = False
            print('good try')
            return True
        except:
            print('bad try')
            pass
    if s:  
        return False 

if __name__  == '__main__':
    print('Это программа для импортирования. Используйте основную')