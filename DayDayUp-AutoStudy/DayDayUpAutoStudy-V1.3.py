from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import random


class Chrome:
    chrome_driver_path = "C:\\Users\xxxxx\AppData\Local\Google\Chrome\Application" + "\chromedriver.exe"
    browser = webdriver.Chrome(chrome_driver_path)   

class SITE:
    def __init__(self, browser):
        self.HOME_PAGE          = 'https://www.xuexi.cn/'
        self.ARTICLES_LINK      = 'https://www.xuexi.cn/d05cad69216e688d304bb91ef3aac4c6/9a3668c13f6e303932b5e0e100fc248b.html'
        self.THEORY_LINK        = 'https://www.xuexi.cn/d184e7597cc0da16f5d9f182907f1200/9a3668c13f6e303932b5e0e100fc248b.html'
        self.VIDEO_LINK         = 'https://www.xuexi.cn/a191dbc3067d516c3e2e17e2e08953d6/b87d700beee2c44826a9202c75d18c85.html'
        self.MOOC_LINK          = 'https://www.xuexi.cn/f547c0f321ac9a0a95154a21485a29d6/1cdd8ef7bfc3919650206590533c3d2a.html'
        self.SCORES_LINK        = 'https://pc.xuexi.cn/points/my-points.html'
        self.LOGIN_LINK         = 'https://pc.xuexi.cn/points/login.html'
        
        # it is prefer to use database to stroe your links
        self.browser        = browser

class User:
    def __init__(self, browser, site):
        self.browser = browser
        self.site = site

    @staticmethod
    def scroll_bar():
        # scroll article top to down
        for ii in range(0, 2000, 100):    
            js_code = "var q=document.documentElement.scrollTop=" + str(ii)
            browser.execute_script(js_code)
            time.sleep(5)

        # scroll article down to top
        for ii in range(1000, 0, -100):
            js_code = "var q=document.documentElement.scrollTop=" + str(ii)
            browser.execute_script(js_code)
            time.sleep(5)

        # keep this tab active 1 minute
        time.sleep( 5 )

    @staticmethod
    def scroll_to_mid():
        # scroll to mid 
        for i in range(0, 500, 100):
            jscode = "var q=document.documentElement.scrollTop=" + str(i)
            browser.execute_script(jscode)
            time.sleep(2)

    @staticmethod
    def generate_random_list(howmany, amount):
        if amount < howmany:
            return list(range(amount))
            
        target  =   [random.randint(0, amount-1) for idx in range(howmany)]
        t_set   =   set(target)
        while len(t_set) < howmany:
            target.append(random.randint(0, amount-1))
            t_set   =   set(target)        
        return sorted(list(t_set))             

    def login_simulation(self):
        browser = self.browser

        browser.get(self.site.LOGIN_LINK)
        print(self.site.LOGIN_LINK)

        browser.maximize_window()
        jscode = "var q=document.documentElement.scrollTop=1000"
        browser.execute_script(jscode)
        time.sleep(10)

        browser.get(self.site.HOME_PAGE)
        print("log in finished\n")
    
    def get_score(self, scorelink):
        browser =  self.browser
        browser.get(scorelink)
        time.sleep(12)

        totalscorePath = "//span[@class='my-points-points my-points-red']"
        total_score    = browser.find_element_by_xpath(totalscorePath).get_attribute('innerText')

        todayscorePath = "//span[@class='my-points-points']"
        today_score    = browser.find_element_by_xpath(todayscorePath).get_attribute('innerText')

        scorePath      = "//div[@class='my-points-card-text']"
        scores         = browser.find_elements_by_xpath(scorePath)
        for score in scores:
            print(score.get_attribute('innerText'), end="  ||  ")
        print("\n ")
        
        remained    = list()
        for idx,    score in enumerate(scores):
            status,   target    =   score.get_attribute('innerText').split("/")
            delta               =   int(status[0]) - int(target[0])
            remained.append(delta)

        scoreStatus = dict()
        keys = ['log', 'article', 'video', 'articletime', 'videotime']
        for key, value in zip(keys, remained):
            scoreStatus[key] = value
        scoreStatus['todayscore']       =   today_score

        return scoreStatus

    def read_articles(self, articlelink, howmany=6, sleep=30, seq=True):
        browser.get(articlelink)
        time.sleep(20)
        
        articlePath  = "//div[@class='text-wrap']/span[@class='text']"
        articlesIter = browser.find_elements_by_xpath(articlePath)
        articles     = [article for article in articlesIter]
        amount       = len(articles)

        if seq:
            articles = articles[:howmany]
        else:
            if amount > 100:
                amount = 100
            target_list = self.generate_random_list(howmany, amount)
            articles = [articles[idx] for idx in target_list]
        
        for index, article in enumerate(articles):
            print(article.get_attribute('innerText'))
            #
            article.click()
            browser.switch_to.window(browser.window_handles[-1])            
            self.scroll_bar()

            # keep this tab active 1 minute
            time.sleep( sleep )
            #
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            time.sleep( 2 )

        print("finish reading " + str(howmany) + " articles!!") 
    
    def watch_video(self, videolink, howmany=6, sleep=60):
        browser = self.browser    
        browser.get(videolink)
        time.sleep(20)
        
        activepagePath  =   "//div[@class='btn active']"
        activePage      =   browser.find_element_by_xpath(activepagePath)

        pagePath        =   "//div[@class='btn']"
        pages           =   browser.find_elements_by_xpath(pagePath)

        videoPath       =   "//div[@class='text-wrap']/span[@class='text']"
        videos          =   browser.find_elements_by_xpath(videoPath)
        for idx, video in enumerate(videos):
            title = video.get_attribute("innerText")
            print( title )

            # only browser 6 videos everyday
            if idx > howmany-1:
                break

            backtab = browser.window_handles[0]
            self.watch_one_video(video, sleep, backtab)

        print("scrapy 6 videos finished!!!")
    
    def watch_one_video(self, video, sleep, backtab):
        browser = self.browser

        video.click()
        browser.switch_to.window(browser.window_handles[-1])

        # set video in midle
        self.scroll_to_mid()

        videoPath       = "//span[@class='duration']"
        videoduration   = browser.find_element_by_xpath(videoPath).get_attribute("innerText")
        minute, second  = videoduration.split(":")
        duration        = int(minute)*60 + int(second)

        if duration > sleep:
            time.sleep(sleep)
        else:
            time.sleep(duration)

        browser.close()
        browser.switch_to.window(backtab)
        time.sleep( 2 )

    def read_mooc(self, mooclink, howmany=6, sleep=90): 
        browser     =   self.browser 
        browser.get(mooclink)
        time.sleep(8)

        lessonPath      = "//div[@class='text-wrap']/span[@class='text']"
        lessonsIter     = browser.find_elements_by_xpath(lessonPath)
        lessons         = [lesson for lesson in lessonsIter]

        count           = len(lessons)
        which   =   random.randint(0, count-1)
        lesson  = lessons[which]
        print(lesson.get_attribute('innerText'))
        self.learn_mooc(lesson, howmany, sleep)

    def learn_mooc(self, lesson, howmany, sleep):
        browser     =   self.browser 
        lesson.click()
        time.sleep(10)
        browser.switch_to.window(browser.window_handles[-1])

        chapterID       =   "//div[@id='Ckwvxzzjntlo00']"
        chaptersIter    =   browser.find_elements_by_xpath(chapterID)
        chapters        =   [chapter for chapter in chaptersIter]
        
        count       =   len(chapters)
        print("chapter amount is %d" % count)

        chapter_ids = self.generate_random_list(howmany, count)
        for which in chapter_ids:
            whichchapter    =   chapters[which]
            print(whichchapter.get_attribute('innerText'))

            backtab  =  browser.window_handles[-1]
            self.watch_one_video(whichchapter, sleep, backtab)
        # back to mooc homelink
        browser.switch_to.window(browser.window_handles[0]) 
 
if __name__ == "__main__":
    chrome  = Chrome()
    browser = chrome.browser

    site    = SITE(browser)
    articlelink =   site.ARTICLES_LINK
    videolink   =   site.VIDEO_LINK
    homepage    =   site.HOME_PAGE
    mooclink    =   site.MOOC_LINK

    usrPage = User(browser, site)
    usrPage.login_simulation()

    art       = 1
    art_time  = 3
    video     = 2
    vid_time  = 4

    for ii in range(2):
        scoreStatus     =   usrPage.get_score(site.SCORES_LINK)
        values = []
        for key, value in scoreStatus.items():
            values.append(value)

        if values[art] < 0 or values[art_time] < 0:
            value = -min([values[art], values[art_time]])
            if ii==0:
                usrPage.read_articles(articlelink, value, 60)
                # usrPage.read_articles(homepage, value, 60, seq=False)
            else:
                usrPage.read_articles(homepage, value, 60, seq=False)
    
        if values[video] < 0 or values[vid_time] < 0:
            value = -min([values[video], values[vid_time]])
            if ii==0:
                usrPage.watch_video(videolink, value, 180)
                # usrPage.read_mooc(mooclink, value, 180) 
            else:
                usrPage.read_mooc(mooclink, value, 180)     
            
    print(usrPage.get_score(site.SCORES_LINK))