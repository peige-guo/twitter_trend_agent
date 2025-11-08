#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Adapted for X (Twitter) scraping
# Date: 2025-11-05

import json
import asyncio
import os
from typing import List, Dict
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from twikit import Client
    TWIKIT_AVAILABLE = True
except ImportError:
    TWIKIT_AVAILABLE = False
    print("Warning: twikit not installed. Please install with: pip install twikit")


class TwitterScraper:
    """
    A class to scrape X (Twitter) data using twikit library.
    """
    
    def __init__(self):
        self.client = None
        if TWIKIT_AVAILABLE:
            self.client = Client('en-US')
    
    async def initialize(self):
        """
        Initialize the Twitter client with cookie-based authentication.
        Uses saved cookies if available, otherwise logs in with credentials from .env file.
        """
        if not TWIKIT_AVAILABLE:
            raise ImportError("twikit library is not available")
        
        cookie_file = 'twitter_cookies.json'
        
        try:
            # Check if cookie file exists and try to load it
            if os.path.exists(cookie_file):
                self.client.load_cookies(cookie_file)
                print("✓ Loaded existing Twitter session cookies")
            else:
                # First time: Login with credentials from environment variables
                username = os.getenv('TWITTER_USERNAME')
                email = os.getenv('TWITTER_EMAIL')
                password = os.getenv('TWITTER_PASSWORD')
                
                if not all([username, email, password]):
                    raise ValueError(
                        "Twitter credentials not found in .env file. "
                        "Please add TWITTER_USERNAME, TWITTER_EMAIL, and TWITTER_PASSWORD"
                    )
                
                print("Logging in to Twitter (first time setup)...")
                await self.client.login(
                    auth_info_1=username,
                    auth_info_2=email,
                    password=password
                )
                
                # Save cookies for future use
                self.client.save_cookies(cookie_file)
                print("✓ Successfully logged in and saved session cookies")
                
        except Exception as e:
            print(f"✗ Twitter authentication failed: {str(e)}")
            print("Please check your credentials in the .env file")
            raise
    
    async def search_tweets(self, keyword: str, count: int = 20) -> List[Dict]:
        """
        Search for tweets by keyword.
        
        Args:
            keyword (str): The search keyword
            count (int): Number of tweets to fetch
            
        Returns:
            List[Dict]: List of tweet data dictionaries
        """
        if not self.client:
            return []
        
        try:
            # Search for tweets
            tweets = await self.client.search_tweet(keyword, 'Latest', count=count)
            
            tweet_list = []
            for tweet in tweets:
                tweet_data = {
                    "tweet_id": getattr(tweet, 'id', ''),
                    "author": getattr(tweet, 'user', {}).name if hasattr(tweet, 'user') else 'Unknown',
                    "author_username": getattr(tweet, 'user', {}).screen_name if hasattr(tweet, 'user') else 'unknown',
                    "author_id": getattr(tweet, 'user', {}).id if hasattr(tweet, 'user') else '',
                    "text": getattr(tweet, 'text', ''),
                    "created_at": getattr(tweet, 'created_at', ''),
                    "likes": getattr(tweet, 'favorite_count', 0),
                    "retweets": getattr(tweet, 'retweet_count', 0),
                    "replies": getattr(tweet, 'reply_count', 0),
                    "views": getattr(tweet, 'view_count', 0),
                    "tweet_url": f"https://x.com/{getattr(tweet, 'user', {}).screen_name if hasattr(tweet, 'user') else 'i'}/status/{getattr(tweet, 'id', '')}",
                }
                
                # Extract hashtags
                hashtags = re.findall(r'#\w+', tweet_data['text'])
                tweet_data['hashtags'] = hashtags
                
                # Extract mentions
                mentions = re.findall(r'@\w+', tweet_data['text'])
                tweet_data['mentions'] = mentions
                
                tweet_list.append(tweet_data)
            
            return tweet_list
        
        except Exception as e:
            print(f"Error searching tweets: {str(e)}")
            return []
    
    async def get_trending_topics(self) -> List[str]:
        """
        Get trending topics/hashtags.
        
        Returns:
            List[str]: List of trending topics
        """
        if not self.client:
            return []
        
        try:
            trends = await self.client.get_trends('worldwide')
            return [trend.name for trend in trends[:10]]
        except Exception as e:
            print(f"Error getting trends: {str(e)}")
            return []


async def process_tweet_results(tweets: List[Dict]) -> str:
    """
    Process tweet results and format them for document storage.
    
    Args:
        tweets (List[Dict]): List of tweet dictionaries
        
    Returns:
        str: JSON formatted string of processed tweets
    """
    processed_tweets = []
    
    for tweet in tweets:
        # Format tweet data for display
        headers = [
            "Type", "Author", "Username", "Tweet Link", "Content", 
            "Published Time", "Likes", "Retweets", "Replies", "Views", 
            "Hashtags", "Mentions"
        ]
        
        processed_data = [
            "tweet",
            tweet.get('author', 'Unknown Author'),
            f"@{tweet.get('author_username', 'unknown')}",
            tweet.get('tweet_url', 'No Link'),
            tweet.get('text', 'No Content'),
            tweet.get('created_at', 'Unknown Time'),
            tweet.get('likes', 0),
            tweet.get('retweets', 0),
            tweet.get('replies', 0),
            tweet.get('views', 0),
            ', '.join(tweet.get('hashtags', [])),
            ', '.join(tweet.get('mentions', []))
        ]
        
        result_text = '\n'.join(f"{header}: {data}" for header, data in zip(headers, processed_data))
        processed_tweets.append(result_text)
    
    return json.dumps(processed_tweets, ensure_ascii=False)


async def twitter_detail_pipeline(keywords: List[str], page: int = 1) -> List[Dict]:
    """
    Main pipeline to fetch and process Twitter data.
    
    Args:
        keywords (List[str]): List of keywords to search
        page (int): Page number (for pagination, currently unused)
        
    Returns:
        List[Dict]: List of dictionaries with keyword and processed data
    
    Raises:
        RuntimeError: If Twitter access is unavailable
    """
    scraper = TwitterScraper()
    
    if not TWIKIT_AVAILABLE:
        raise RuntimeError("No access to X: twikit library is not installed. Please install with: pip install twikit")
    
    try:
        await scraper.initialize()
    except Exception as e:
        raise RuntimeError(f"No access to X: Authentication failed - {str(e)}")
    
    all_results = []
    
    for keyword in keywords:
        print(f"Searching for keyword: {keyword}")
        
        try:
            # Fetch tweets for this keyword
            tweets = await scraper.search_tweets(keyword, count=20)
            
            if not tweets:
                print(f"No tweets found for keyword: {keyword}")
                continue
            
            # Process the tweets
            real_data = await process_tweet_results(tweets)
            
            all_results.append({
                "keyword": keyword,
                "real_data": real_data
            })
        
        except Exception as e:
            print(f"Error processing keyword '{keyword}': {str(e)}")
            continue
    
    if not all_results:
        raise RuntimeError("No access to X: Failed to retrieve any tweets. Twitter may be blocking requests.")
    
    print(f"all_results: {json.dumps(all_results, indent=4, ensure_ascii=False)}")
    return all_results


if __name__ == '__main__':
    # Test the scraper
    async def main():
        try:
            results = await twitter_detail_pipeline(keywords=["AI trends", "machine learning"], page=1)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        except RuntimeError as e:
            print(f"Error: {e}")
    
    asyncio.run(main())

