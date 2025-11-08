#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Adapted for X (Twitter) API v2
# Date: 2025-11-08

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
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Warning: tweepy not installed. Please install with: pip install tweepy")


class TwitterAPIClient:
    """
    A class to interact with X (Twitter) data using Twitter API v2.
    """
    
    def __init__(self):
        self.client = None
        self.api_initialized = False
    
    def initialize(self):
        """
        Initialize the Twitter API client with Bearer Token authentication.
        Uses Twitter API v2 credentials from .env file.
        
        Note: You need to have a Twitter Developer account and create an app at:
        https://developer.twitter.com/en/portal/dashboard
        """
        if not TWEEPY_AVAILABLE:
            raise ImportError("tweepy library is not available")
        
        # Get credentials from environment variables
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Alternative: Use API keys (v1.1 style authentication)
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        try:
            # Prefer Bearer Token for API v2 (simpler, read-only access)
            if bearer_token:
                print("✓ Using Bearer Token authentication for Twitter API v2")
                self.client = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=True
                )
            # Fallback to OAuth 1.0a with API keys
            elif all([api_key, api_secret, access_token, access_token_secret]):
                print("✓ Using OAuth 1.0a authentication for Twitter API")
                self.client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    wait_on_rate_limit=True
                )
            else:
                raise ValueError(
                    "Twitter API credentials not found in .env file.\n"
                    "Please add either:\n"
                    "  - TWITTER_BEARER_TOKEN (recommended for read-only access), or\n"
                    "  - TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, "
                    "and TWITTER_ACCESS_TOKEN_SECRET\n\n"
                    "Get your credentials at: https://developer.twitter.com/en/portal/dashboard"
                )
            
            self.api_initialized = True
            print("✓ Twitter API client initialized successfully")
            
        except Exception as e:
            print(f"✗ Twitter API authentication failed: {str(e)}")
            raise
    
    def search_tweets(self, keyword: str, count: int = 20) -> List[Dict]:
        """
        Search for tweets by keyword using Twitter API v2.
        
        Args:
            keyword (str): The search keyword
            count (int): Number of tweets to fetch (max 100 per request)
            
        Returns:
            List[Dict]: List of tweet data dictionaries
        """
        if not self.client or not self.api_initialized:
            raise RuntimeError("Twitter API client not initialized. Call initialize() first.")
        
        try:
            # Use Twitter API v2 search_recent_tweets
            # Tweet fields to retrieve
            tweet_fields = [
                'id', 'text', 'author_id', 'created_at',
                'public_metrics', 'entities', 'lang'
            ]
            
            # User fields to retrieve
            user_fields = ['id', 'name', 'username']
            
            # Expansions to get additional data
            expansions = ['author_id']
            
            # Search for tweets
            response = self.client.search_recent_tweets(
                query=keyword,
                max_results=min(count, 100),  # API limit is 100
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                expansions=expansions
            )
            
            if not response.data:
                print(f"No tweets found for keyword: {keyword}")
                return []
            
            # Create a user lookup dictionary
            users = {}
            if response.includes and 'users' in response.includes:
                for user in response.includes['users']:
                    users[user.id] = user
            
            tweet_list = []
            for tweet in response.data:
                # Get user information
                user = users.get(tweet.author_id)
                author_name = user.name if user else 'Unknown'
                author_username = user.username if user else 'unknown'
                
                # Get public metrics
                metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
                
                # Extract hashtags and mentions from entities
                hashtags = []
                mentions = []
                if hasattr(tweet, 'entities') and tweet.entities:
                    if 'hashtags' in tweet.entities:
                        hashtags = [f"#{tag['tag']}" for tag in tweet.entities['hashtags']]
                    if 'mentions' in tweet.entities:
                        mentions = [f"@{mention['username']}" for mention in tweet.entities['mentions']]
                
                tweet_data = {
                    "tweet_id": str(tweet.id),
                    "author": author_name,
                    "author_username": author_username,
                    "author_id": str(tweet.author_id),
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if hasattr(tweet, 'created_at') else datetime.now().isoformat(),
                    "likes": metrics.get('like_count', 0),
                    "retweets": metrics.get('retweet_count', 0),
                    "replies": metrics.get('reply_count', 0),
                    "views": metrics.get('impression_count', 0),  # Note: impression_count may require elevated access
                    "tweet_url": f"https://x.com/{author_username}/status/{tweet.id}",
                    "hashtags": hashtags,
                    "mentions": mentions
                }
                
                tweet_list.append(tweet_data)
            
            return tweet_list
        
        except tweepy.TweepyException as e:
            print(f"Twitter API error: {str(e)}")
            raise RuntimeError(f"Twitter API error: {str(e)}")
        except Exception as e:
            print(f"Error searching tweets: {str(e)}")
            raise RuntimeError(f"Error searching tweets: {str(e)}")
    
    def get_trending_topics(self, woeid: int = 1) -> List[str]:
        """
        Get trending topics/hashtags.
        
        Note: This requires API v1.1 endpoints which may need elevated access.
        
        Args:
            woeid (int): Where On Earth ID (1 = Worldwide, 23424977 = United States)
            
        Returns:
            List[str]: List of trending topics
        """
        print("Note: Trending topics require Twitter API v1.1 and may need elevated access")
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


async def twitter_detail_pipeline(keywords: List[str], page: int = 1, count: int = 20) -> List[Dict]:
    """
    Main pipeline to fetch and process Twitter data using official API.
    
    Args:
        keywords (List[str]): List of keywords to search
        page (int): Page number (for pagination, currently unused in API v2)
        count (int): Number of tweets to fetch per keyword (default: 20, max: 100)
        
    Returns:
        List[Dict]: List of dictionaries with keyword and processed data
    
    Raises:
        RuntimeError: If Twitter API access is unavailable
    """
    client = TwitterAPIClient()
    
    if not TWEEPY_AVAILABLE:
        raise RuntimeError("No access to X: tweepy library is not installed. Please install with: pip install tweepy")
    
    try:
        client.initialize()
    except Exception as e:
        raise RuntimeError(f"No access to X: API authentication failed - {str(e)}")
    
    all_results = []
    
    for keyword in keywords:
        print(f"Searching for keyword: {keyword}")
        
        try:
            # Fetch tweets for this keyword
            tweets = client.search_tweets(keyword, count=count)
            
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
        raise RuntimeError("No access to X: Failed to retrieve any tweets. Please check your API credentials and rate limits.")
    
    print(f"all_results: {json.dumps(all_results, indent=4, ensure_ascii=False)}")
    return all_results


if __name__ == '__main__':
    # Test the API client
    async def main():
        try:
            results = await twitter_detail_pipeline(keywords=["AI trends", "machine learning"], page=1)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        except RuntimeError as e:
            print(f"Error: {e}")
    
    asyncio.run(main())
