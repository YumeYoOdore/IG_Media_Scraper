# IG_Media_Scraper
A Scraper to download images and video files from IG using Selenium: personal exercise to learn Selenium and XPath

General notes for IG_Scraper.py

3 types of scrapers:
(1) per IG user page (not advisable, too many requests, risking getting IP blocked)
(2) per Photo page (more advisable, not so many requests, although if entering a lot of pages in a short period may also get IP blocked)
(3) stories scraper

My guidelines, thought process on the tool design

for (1)
1. Load user page
2. Scroll to the very end. Hint: use browserObj.execute_script("window.scrollTo(0, document.body.scrollHeight);")
3. while scrolling down querying the HTML tree for every post (posts have "/p/" in url)
4. store all posts links in a list and start iterating through them using (2)
4.1 alternarively, save the URLs list in a txt file and use it later on to run (2) without sending too many requests to IG server

for (2)
1. Load post page
2. check if it has more than one photo or only one
2.a in case it only has one photo problem is trivial, just find xpath with tag "img" (store it in a singleton list)
    (Update post-tool completion: there are a lot of items with img tag, had to find the main container and from there find the exact img tag to get the url from)
2.b in case it has more than one photo will have to start gathering all links, check if the page has a "next" arrow object
2.b.i click the "next" arrow object and start looking for items in xpath with tag "img"
    (Update post-tool completion: same as in 2.a; however by solving the problem for one single image, problem is already solved for more than one item)
2.b.ii start saving the items in a list, can always make sure if the list already has the item to avoid duplicates
3. from the pic element list start iterating through each element to start downloading the pictures with wget

for (3)
1. Load user page
2. Have selenium click the user pfp to redirect to stories page
3. Since stories have very few elements we only need to get the container where the main media is rendered
4. Query on main media container for either picture or image and similar to (2) save the results in a list to later download with wget

Final notes:
Originally the tool was thought to only download pictures, but since the code stays the same for video (with few changes) it was expanded to also get video content
(therefore the notes for (1) and (2) only mention "img", wording changes to media later on as video functionality was also included) same goes for the stories scraper
portion, it wasn't originally intended but the code could be reusable so functionality was built.

Tool took me 3 full days of work to make, while it still can undergo a lot of optimizations, as this isn't a professional work/tool and it's creation was ONLY intended
for a) Personal use. b) Learning a new tool/library (Selenium). c) Having something to do while getting out of an art creative block. I don't have further plans for this,
uploading this tool to GitHub as it can be helpful for other people who may be in the process of learning either Python or Selenium.
Most of my code here presented is already available on the internet, but in any case if you intend to use it on a non-personal project (i.e. work or an app you're developing))
at the very least please give me a follow: would appreciate a bit more some love on my Artstation rather than my Github
in any case adding my social media handles here in case you want to show some appreciation for this:

Youtube: https://www.youtube.com/@dreamrider7128
Artstation:  https://www.artstation.com/dreamrider712
Itch.io: https://dreamrider.itch.io/
Twitter: https://twitter.com/DreamRider712

Disclaimer: Keep in mind that most of the tags used in this tool may change in the future which may render the current version unusable, if that's the case only have to review
the tags used by IG