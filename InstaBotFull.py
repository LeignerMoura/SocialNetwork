import random
import time
import datetime
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class InstagramBot:

    def __init__(self, username, password, caminho):
        self.username = username
        self.password = password
        self.driver = webdriver.Firefox(executable_path=r'C:\Users\lmoura\Desktop\geckodriver\geckodriver.exe')
        self.caminho = caminho

    @staticmethod
    def inserir_csv(arquivo, lista, tipo):
        # Insere usuarios principais (curtidos e comentados)
        listausuarios = [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ';' + lin + ';' + tipo for
                         lin in lista]
        with open(arquivo, 'a', newline='\n') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\n', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(listausuarios)

    def closeBrowser(self):
        self.driver.close()

    def login(self):

        driver = self.driver
        driver.get("https://www.instagram.com/")
        time.sleep(2)

        user_name_elem = driver.find_element_by_xpath("//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)

        # password field and fill
        password_elem = driver.find_element_by_xpath("//input[@name='password']")
        password_elem.clear()
        password_elem.send_keys(self.password)

        # simula a tecla enter
        password_elem.send_keys(Keys.RETURN)
        time.sleep(2)

    def get_valid_photo_links(self, hashtags):
        driver = self.driver
        # esvazia a lista
        pic_hrefs = []

        for hashtag in hashtags:
            driver.get('https://www.instagram.com/explore/tags/' + hashtag + '/')
            time.sleep(2)

            # bot scrolls down to web page to get new pictures
            for i in range(1, 3):
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    # get all the tags
                    hrefs_in_view = driver.find_elements_by_tag_name('a')
                    # finding relevant hrefs
                    pics_in_view = [elem.get_attribute('href') for elem in hrefs_in_view if
                                    '.com/p/' in elem.get_attribute('href')]
                    # building list of unique photos
                    [pic_hrefs.append(href) for href in pics_in_view if href not in pic_hrefs]
                    print(hashtag + ' photos: ' + str(len(pic_hrefs)))
                except Exception:
                    continue

        return pic_hrefs

    def like_photo(self):
        #try:
        like_button = self.driver.find_element_by_css_selector('.fr66n > button:nth-child(1)')
        like_button.click()
        print('Liked!')

        #except Exception as e:
        #    time.sleep(2)

    def comment(self, comentarios):
        comments = comentarios
        try:
            comment_field = lambda: self.driver.find_element_by_tag_name('textarea')
            comment_field().click()
            comment_field().clear()

            comment = random.choice(comments)
            for letter in comment:
                comment_field().send_keys(letter)
                time.sleep(random.randint(1, 9) / 10)

            comment_field().send_keys(Keys.RETURN)
        except Exception as e:
            print(e)
            time.sleep(2)


    def execute(self, hashtags, comentarios, curtir, comentar):
        pic_hrefs = self.get_valid_photo_links(hashtags)
        unique_photos = len(pic_hrefs)

        for link in pic_hrefs:

            # Vai no perfil selecionado
            self.driver.get(link)
            time.sleep(random.randint(1, 3))
            # scrolldown
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(2, 4))
            # scrollup
            self.driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
            time.sleep(random.randint(2, 4))
            # Curti foto
            if curtir == True:
                self.like_photo()
                time.sleep(random.randint(2, 4))

            # chama a ação de comentar
            if comentar == True:
                self.comment(comentarios)
                time.sleep(random.randint(2, 4))


            #desativei a curtida de pessoas derivadas
            #self.see_who_liked_and_like(link)

            unique_photos -= 1
            sleep_time = random.randint(18, 28)
            print('# of unique photos left: ' + str(unique_photos) + ' sleeping for ' + str(sleep_time))
            time.sleep(sleep_time)

        # Insere usuarios principais (curtidos e comentados)
        self.inserir_csv(caminho + 'Curtidos.csv', pic_hrefs, 'Principal')

        self.closeBrowser()

    def see_who_liked_and_like(self, link):
        users_link = []
        self.driver.get(link)
        time.sleep(2)

        # click to view who liked.        class="sqdOP yWX7d     _8A5w5    "
        liked_by_button = lambda: self.driver.find_element_by_xpath('//button[@class="sqdOP yWX7d     _8A5w5    "]')
        liked_by_button().click()
        time.sleep(3)

        # get users' profile links .     class="_2dbep qNELH kIKUG" for user tag
        hrefs_in_view = self.driver.find_elements_by_xpath('//a[@class="_2dbep qNELH kIKUG"]')
        # getting the hrefs
        links = [elem.get_attribute('href') for elem in hrefs_in_view]
        # building list of unique photos
        [users_link.append(href) for href in links if href not in users_link]

        # Insere usuarios secundarios (curtidos)
        self.inserir_csv(caminho + 'Curtidos.csv', users_link, 'Secundarios')

        # now go through the valid user profile links and like their first pic
        for link in users_link:
            self.driver.get(link)
            time.sleep(2)

            # get all the link tags on the page
            hrefs_in_view = self.driver.find_elements_by_tag_name('a')
            # finding relevant hrefs
            posts_in_view = [elem.get_attribute('href') for elem in hrefs_in_view if
                             '.com/p/' in elem.get_attribute('href')]

            if len(posts_in_view) > 0:
                first_post = posts_in_view[0]
                self.driver.get(first_post)
                time.sleep(random.randint(1, 3))
                self.like_photo()
                time.sleep(random.randint(2, 4))


if __name__ == "__main__":
    caminho = 'C:/Users/lmoura/Desktop/bot/'

    myfile = open(caminho + 'SenhaInsta.txt', 'rt')
    # line != '' significa que esta tirando linhas em branco da lista
    perfil = [line for line in myfile.read().splitlines() if line != '']
    myfile.close()

    myfile2 = open(caminho + 'BotHashtags.txt', 'rt')
    listaHashtags = [line2 for line2 in myfile2.read().splitlines() if line2 != '']
    myfile2.close()

    # encoding='utf8' metodo de leitura para aceitar emoji
    myfile3 = open(caminho + 'Comentarios.txt', 'r', encoding='utf8')
    comentarios = [line3 for line3 in myfile3.read().splitlines() if line3 != '']
    myfile3.close()

    username = perfil[0]
    pw = perfil[1]

    print(f'Usuário: {username} \nSenha: {pw} \nLista de #: {str(listaHashtags)} \nComentários: {str(comentarios)}')
#botao erro /html/body/div[4]/div/div/div[2]/button[1]
    ig = InstagramBot(username, pw, caminho)
    ig.login()
    ig.execute(listaHashtags, comentarios, True, False)

    # ig.see_who_liked_and_like('https://www.instagram.com/p/B3vVZxfJMyv/')
