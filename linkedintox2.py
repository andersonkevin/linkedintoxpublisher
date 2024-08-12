import requests
from bs4 import BeautifulSoup
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# File to store posted LinkedIn article URLs
POSTED_ARTICLES_FILE = 'posted_articles.json'

def load_posted_articles():
    """Load the list of posted LinkedIn articles from the file."""
    if os.path.exists(POSTED_ARTICLES_FILE):
        with open(POSTED_ARTICLES_FILE, 'r') as file:
            return json.load(file)
    return []

def save_posted_articles(posted_articles):
    """Save the list of posted LinkedIn articles to the file."""
    with open(POSTED_ARTICLES_FILE, 'w') as file:
        json.dump(posted_articles, file)

def get_linkedin_articles(linkedin_url):
    """Scrape LinkedIn articles from the provided URL."""
    try:
        response = requests.get(linkedin_url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract LinkedIn article URLs
        article_links = []
        for link in soup.find_all('a', href=True):
            if 'linkedin.com/pulse/' in link['href']:
                full_url = link['href']
                if not full_url.startswith('https://'):
                    full_url = f'https://www.linkedin.com{full_url}'
                article_links.append(full_url)
        
        return article_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching LinkedIn articles: {e}")
        return []

def get_twitter_links_v2(bearer_token, user_id, tweet_count=100):
    """Fetch recent tweets using Twitter API v2."""
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={tweet_count}&tweet.fields=entities"
    print(f"Fetching tweets from URL: {url}")
    print(f"Using headers: {headers}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        tweets = response.json()
        tweet_links = []

        if 'data' in tweets:
            for tweet in tweets['data']:
                if 'entities' in tweet and 'urls' in tweet['entities']:
                    for url in tweet['entities']['urls']:
                        tweet_links.append(url['expanded_url'])
        
        return tweet_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Twitter links: {e}")
        print(f"Response content: {response.text}")
        return []

def post_to_twitter(bearer_token, tweet_text):
    """Post a tweet to Twitter."""
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": tweet_text
    }
    
    print(f"Posting to Twitter with payload: {payload}")
    print(f"Using headers: {headers}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        print(f"Successfully posted tweet: {tweet_text}")
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Twitter: {e}")
        print(f"Response content: {response.text}")

def main():
    linkedin_url = "https://www.linkedin.com/today/author/andersonkev?trk=public_profile_see-all-articles"
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")  # Load from environment variable
    user_id = os.getenv("TWITTER_USER_ID")  # Load from environment variable

    # Load the list of already posted articles
    posted_articles = load_posted_articles()

    # Step 1: Get LinkedIn articles
    linkedin_articles = get_linkedin_articles(linkedin_url)

    # Step 2: Get tweets from Twitter
    twitter_links = get_twitter_links_v2(bearer_token, user_id)

    # Step 3: Compare and post missing articles
    for article in linkedin_articles:
        if article not in twitter_links and article not in posted_articles:
            post_to_twitter(bearer_token, article)
            posted_articles.append(article)

    # Step 4: Save the updated list of posted articles
    save_posted_articles(posted_articles)

if __name__ == "__main__":
    main()
