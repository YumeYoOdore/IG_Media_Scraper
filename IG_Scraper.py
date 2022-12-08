import sys
import argparse

from WebDriverTorso import WebDriverTorso

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
