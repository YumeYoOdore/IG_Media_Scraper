import os
import wget
import sys
import argparse
import time

from decouple import config

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

class WebDriverTorso:
    def __init__(self, target_url, additional_options):
        self.img_urls = []
        self.video_urls = []
        self.posts_urls = []
        self.user_name = ''
        
        self.options = Options()
        
        #forcing webdriver to run on en locale to avoid issues with html text in other languages (in my case Spanish)
        self.options.set_preference('intl.accept_languages', 'en-US')
        self.options.headless = True
        self.firstTimeLoad = False

        self.getUserStories = additional_options.get('get_stories')
        #In case the page we want to access requires us to login will call the proper function to login
        self.requiresLogIn = additional_options.get('requires_login')
        self.recursiveDownload = additional_options.get('recusive_download')
        
        self.target_url = target_url

        #due to my local environment I'm using this without sending the geckodriver location
        self.driver = webdriver.Firefox(options=self.options) 
        #when running this tool use the following one and change %PATH%TO%GECKODRIVER to your actual geckodriver path
        #self.driver = webdriver.Firefox(%PATH%TO%GECKODRIVER, options=self.options)

        print("Headless firefox initialized")

    
    def login(self):
        self.driver.get(config('IG_MAIN_PAGE'))
        username = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        password = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

        username.clear()
        password.clear()

        username.send_keys(config('USERNAME'))
        password.send_keys(config('PASSWORD'))

        login = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        not_now = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(('xpath', '//button[contains(text(), "Not Now")]'))).click()


    def get_target_user_info(self):
        class_tag_string = config('TARGET_INFO_TAG_STR')
        try:
            self.user_name = self.driver.find_elements('xpath', '//a[contains(@class, "%s")]' % class_tag_string)[0].text
        except:
            print("Error retrieving poster username")


    def get_media_urls(self):
        found_img_elements = []
        found_video_elements = []

        try:
            #Trying to find the main container through xpath to avoid downloading images from other preview posts and pfps from comments
            main_container_obj = self.driver.find_elements("xpath", "//div[@class = '_aa6e']//div[@class = '_aagv']")

            #1. Try to get all pictures in post
            for container_obj in main_container_obj:
                img_elements = container_obj.find_elements(By.TAG_NAME, 'img')
                
                if img_elements:
                    for element in img_elements:
                        out_url = element.get_attribute('src')
                        found_img_elements.append(out_url)
            
            #2. Try to get all videos in post
            video_elements = self.driver.find_element("xpath", "//div[@class = '_aa6e']").find_elements(By.TAG_NAME, "video")

            if video_elements:
                for element in video_elements:
                    out_url = element.get_attribute('src')
                    found_video_elements.append(out_url)
        except:
            print("Couldn't retrieve main container, either doesn't exist or is no longer attached to the DOM")

        return found_img_elements, found_video_elements

    
    def get_output_filename(self, file_extention, post_url_string):
        #used to construct the output filename based on the file to download
        #convention I came up with: 
        #"{user_name}_IG_{media_type}_download_{post_key}.{file_extention}
        output_filename = ''
        
        file_type = 'video' if file_extention == "mp4" else "image"
        output_filename = f'{self.user_name}_IG_{file_type}_download_{post_url_string}.{file_extention}'
        return output_filename 


    def save_files(self, post_url_string):
        #this can also be handled in bash
        path = os.getcwd()
        save_dir = os.path.join(path, "save_dir", self.user_name + "_downloads")

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        counter = 0

        #for saving image files
        for url in self.img_urls:
            file_extention = "jpg"

            output_filename = self.get_output_filename(file_extention, post_url_string + "_" + str(counter))

            save_as = os.path.join(save_dir, output_filename)
            wget.download(url, save_as)
            counter += 1

        counter = 0

        #for saving video files
        for url in self.video_urls:
            file_extention = "mp4"

            output_filename = self.get_output_filename(file_extention, post_url_string + "_" + str(counter))

            save_as = os.path.join(save_dir, output_filename)
            wget.download(url, save_as)
            counter += 1


    def user_stories_scrape(self):
        last_media_found = False
        post_url_string = self.driver.current_url.split('/')[-2]

        stories_button = self.driver.find_element('xpath', '//div[@class = "_aarf _aarg"]')
        if stories_button:
            stories_button.click()
            self.driver.implicitly_wait(2)

        while not last_media_found:
            try:
                img_element = self.driver.find_element('xpath', '//div[@class = "_aa64"]').find_element(By.TAG_NAME, 'img').get_attribute('src')
                if "blob" in video_element:
                    print("blob object found, not supported by this scraper")
                else:
                    if img_element and img_element not in self.img_urls:
                        self.img_urls.append(img_element) 
            except:
                print("Current story does not contain any picture")

            try:
                video_element = self.driver.find_element(By.TAG_NAME, 'video').get_attribute('src')
                if "blob" in video_element:
                    print("blob object found, not supported by this scraper")
                else:
                    if video_element and video_element not in self.img_urls:
                        self.video_urls.append(video_element)
            except:
                print("Current story does not contain any video")

            try:
                next_button = self.driver.find_element('xpath', '//button[@class = "_ac0d"]')
                if next_button:
                    next_button.click()
                    self.driver.implicitly_wait(1)
            except:
                last_media_found = True
                print("No next_button found : page only has one media item or already at last media, returning")

        self.save_files(post_url_string)


    def get_posts_in_profile(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        extracted_urls = []

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(0.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            try:
                show_more_posts_btn = self.driver.find_element('xpath', '//button//div[contains(text(), "Show more posts from")]')
                if show_more_posts_btn:
                    show_more_posts_btn.click()
                    self.driver.implicitly_wait(1)
            except:
                pass

            #attempt to retrieve all posts while scrolling down
            links = self.driver.find_elements('xpath', '//a[contains(@href, "/p/")]')
            extracted_urls.extend(links)
            
            last_height = new_height

        for url in extracted_urls:
            link = url.get_attribute('href')
            if link not in self.posts_urls:
                self.posts_urls.append(link)
                
        print(f'Scroll height: {last_height}')
        print("Reached end of page, extracted links :")
        for url in self.posts_urls:
            print(url)


    def post_pic_scrape(self):
        last_media_found = False

        while not last_media_found:
            img_element_list, video_element_list = self.get_media_urls()

            self.img_urls.extend((element for element in img_element_list if element not in self.img_urls))
            self.video_urls.extend((element for element in video_element_list if element not in self.video_urls))

            try:
                next_button = self.driver.find_element('xpath', '//button[@class = " _afxw"]')
                if next_button:
                    next_button.click()
                    self.driver.implicitly_wait(1)
            except:
                last_media_found = True
                print("No next_button found : page only has one media item or already at last media, returning")

        #in case we're calling this function directly from a post we'll need to retrieve target IG username from selenium
        if not self.user_name:
            self.get_target_user_info()

    
    def run(self):
        #load the page at the beginning of the execution and wait for 5 seconds for page to load
        if self.requiresLogIn:
            self.login()

        self.driver.get(self.target_url)
        self.driver.implicitly_wait(5)

        if '/p/' in self.target_url:
            print("Post url provided, scraping photos from provided post")
            self.post_pic_scrape()
            post_url_string = self.target_url.split('/')[4]
            self.save_files(post_url_string)

        elif self.target_url.endswith('instagram.com/') or self.target_url.endswith('inbox/'):
            print("IG main page provided or invalid IG URL provided, exiting")
            sys.exit(0)
        else:
            self.user_name = self.target_url.split('/')[-2]
            if self.getUserStories:
                self.user_stories_scrape()
            else:
                print("User profile url provided, retrieving all posts from given profile")
                self.get_posts_in_profile()
                if self.recursiveDownload:
                    for url in self.posts_urls:
                        self.img_urls.clear()
                        self.video_urls.clear()

                        self.driver.get(url)
                        self.driver.implicitly_wait(1)

                        self.post_pic_scrape()
                        post_url_string = url.split('/')[4]
                        print(post_url_string)
                                
                        self.save_files(post_url_string)

                else:
                    path = os.getcwd()
                    
                    output_filename = os.path.join(path, f'{self.user_name}_crawled_urls.txt')
                    print(f'Saving crawled URLs to text file {output_filename}')

                    with open(output_filename, 'w') as out_file:
                        out_file.write('\n'.join(self.posts_urls))

        self.driver.quit()


if __name__ == "__main__":
    #run main functionality
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help="Target IG URL to get images from", required=True)
    parser.add_argument('-r', '--recursive', help="Download all posts from a given user (Not advisable as may get IP blocked)", action='store_true')
    parser.add_argument('-s', '--stories', help="Download stories from a given user URL", action='store_true')
    args = parser.parse_args()

    target_url = args.url
    get_stories = args.stories
    recursive_post_download = args.recursive

    additional_options = {
        'get_stories': get_stories,
        'requires_login': False,
        'recusive_download': recursive_post_download
    }
    
    #Check if login is required
    if "/p/" not in target_url or get_stories:
        additional_options['requires_login'] = True

    if not target_url.startswith('https://www.instagram.com/'):
        print("Error: not URL provided is not a IG URL, exiting")
        sys.exit(0)

    scraper = WebDriverTorso(target_url, additional_options)
    scraper.run()
