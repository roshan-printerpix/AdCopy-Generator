"""
Pipeline Entry Point
Single function that orchestrates data collection and passes to cleaning module.
"""

from . import reddit_scraper, web_scraper, api_scraper
from utils.logger import setup_logger

logger = setup_logger("pipeline_entry")

def collect_and_process_data(sources_config):
    """
    Main entry point for data collection pipeline.
    Scrapes content from all configured sources and passes to cleaning module.
    
    Args:
        sources_config (dict): Configuration for different data sources
    
    Returns:
        list: Raw content collected from all sources
    """
    raw_content = []
    
    logger.info("Starting data collection from configured sources...")
    
    # Collect from Reddit (specifically r/ppc)
    if sources_config.get('reddit', {}).get('enabled', True):
        try:
            logger.info("Collecting data from Reddit...")
            reddit_config = sources_config.get('reddit', {})
            
            # Default to r/ppc if no subreddits specified
            subreddits = reddit_config.get('subreddits', ['ppc'])
            limit = reddit_config.get('limit', 50)
            
            # If ppc is in the subreddits list, use the specialized scraper
            if 'ppc' in subreddits:
                logger.info("Using specialized r/ppc scraper...")
                ppc_content = reddit_scraper.scrape_ppc_subreddit(
                    limit=limit,
                    time_filter=reddit_config.get('time_filter', 'week'),
                    sort=reddit_config.get('sort', 'hot'),
                    include_comments=reddit_config.get('include_comments', True),
                    max_comments=reddit_config.get('max_comments', 10)
                )
                raw_content.extend(ppc_content)
                
                # Remove ppc from subreddits list to avoid double scraping
                other_subreddits = [s for s in subreddits if s != 'ppc']
                if other_subreddits:
                    other_content = reddit_scraper.scrape_reddit_posts(
                        subreddits=other_subreddits,
                        keywords=reddit_config.get('keywords'),
                        limit=limit // 2  # Split limit between ppc and others
                    )
                    raw_content.extend(other_content)
            else:
                # Use general scraper for other subreddits
                reddit_content = reddit_scraper.scrape_reddit_posts(
                    subreddits=subreddits,
                    keywords=reddit_config.get('keywords'),
                    limit=limit
                )
                raw_content.extend(reddit_content)
                
            logger.info(f"Collected {len([c for c in raw_content if 'reddit.com' in str(c) or 'Title:' in str(c)])} posts from Reddit")
            
        except Exception as e:
            logger.error(f"Error collecting from Reddit: {e}")
    
    # Collect from web sources
    if sources_config.get('web', {}).get('enabled', False):
        try:
            logger.info("Collecting data from web sources...")
            web_config = sources_config.get('web', {})
            urls = web_config.get('urls', [])
            
            if urls:
                web_content = web_scraper.scrape_blog_posts(urls)
                raw_content.extend(web_content)
                logger.info(f"Collected {len(web_content)} items from web sources")
            
        except Exception as e:
            logger.error(f"Error collecting from web sources: {e}")
    
    # Collect from APIs
    if sources_config.get('apis', {}).get('enabled', False):
        try:
            logger.info("Collecting data from APIs...")
            api_config = sources_config.get('apis', {})
            
            # Twitter/X
            if api_config.get('twitter'):
                twitter_config = api_config['twitter']
                twitter_content = api_scraper.scrape_twitter_posts(
                    hashtags=twitter_config.get('hashtags'),
                    keywords=twitter_config.get('keywords'),
                    limit=twitter_config.get('limit', 20)
                )
                raw_content.extend(twitter_content)
                logger.info(f"Collected {len(twitter_content)} posts from Twitter")
            
        except Exception as e:
            logger.error(f"Error collecting from APIs: {e}")
    
    logger.info(f"Data collection completed. Total items collected: {len(raw_content)}")
    return raw_content

def collect_ppc_data_only(limit=50, time_filter='week', sort='hot', include_comments=True, max_comments=10):
    """
    Simplified function to collect data only from r/ppc.
    
    Args:
        limit (int): Maximum number of posts to scrape
        time_filter (str): Time filter for posts
        sort (str): Sort method for posts
        include_comments (bool): Whether to include comments
        max_comments (int): Maximum number of comments per post
    
    Returns:
        list: Raw content from r/ppc
    """
    logger.info(f"Collecting data from r/ppc only (limit={limit}, include_comments={include_comments})")
    
    try:
        raw_content = reddit_scraper.scrape_ppc_subreddit(
            limit=limit,
            time_filter=time_filter,
            sort=sort,
            include_comments=include_comments,
            max_comments=max_comments
        )
        
        logger.info(f"Successfully collected {len(raw_content)} posts from r/ppc")
        return raw_content
        
    except Exception as e:
        logger.error(f"Error collecting from r/ppc: {e}")
        return []