"""
Reddit Scraper Module
Handles scraping Reddit threads and posts for ad creative insights.
"""

import praw
import time
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger("reddit_scraper")

def get_reddit_client():
    """
    Initialize and return Reddit client using credentials from config.
    Uses read-only mode which doesn't require username/password.
    
    Returns:
        praw.Reddit: Authenticated Reddit client
    """
    try:
        # Try with username/password first
        if Config.REDDIT_USERNAME and Config.REDDIT_PASSWORD:
            try:
                reddit = praw.Reddit(
                    client_id=Config.REDDIT_CLIENT_ID,
                    client_secret=Config.REDDIT_CLIENT_SECRET,
                    user_agent=Config.REDDIT_USER_AGENT,
                    username=Config.REDDIT_USERNAME,
                    password=Config.REDDIT_PASSWORD
                )
                
                # Test authentication
                user = reddit.user.me()
                logger.info(f"Reddit client authenticated as: {user}")
                return reddit
                
            except Exception as e:
                logger.warning(f"Username/password authentication failed: {e}")
                logger.info("Falling back to read-only mode...")
        
        # Fallback to read-only mode (no username/password required)
        reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )
        
        # Test read-only access
        test_subreddit = reddit.subreddit('ppc')
        test_post = next(test_subreddit.hot(limit=1))
        logger.info(f"Reddit client initialized in read-only mode. Test post: {test_post.title[:50]}...")
        
        return reddit
        
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}")
        raise

def scrape_ppc_subreddit(limit=50, time_filter='week', sort='hot', include_comments=True, max_comments=10):
    """
    Scrape posts from r/ppc subreddit specifically, including comments.
    
    Args:
        limit (int): Maximum number of posts to scrape
        time_filter (str): Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
        sort (str): Sort method ('hot', 'new', 'top', 'rising')
        include_comments (bool): Whether to include comments
        max_comments (int): Maximum number of comments to scrape per post
    
    Returns:
        list: Raw text content from r/ppc posts with comments
    """
    try:
        reddit = get_reddit_client()
        subreddit = reddit.subreddit('ppc')
        
        logger.info(f"Scraping r/ppc with limit={limit}, sort={sort}, time_filter={time_filter}, include_comments={include_comments}")
        
        raw_content = []
        posts_processed = 0
        
        # Get posts based on sort method
        if sort == 'hot':
            posts = subreddit.hot(limit=limit)
        elif sort == 'new':
            posts = subreddit.new(limit=limit)
        elif sort == 'top':
            posts = subreddit.top(time_filter=time_filter, limit=limit)
        elif sort == 'rising':
            posts = subreddit.rising(limit=limit)
        else:
            posts = subreddit.hot(limit=limit)
        
        for post in posts:
            try:
                # Skip stickied posts and announcements
                if post.stickied:
                    continue
                
                # Combine title and selftext for full content
                post_content = f"Title: {post.title}\n\n"
                
                if post.selftext:
                    post_content += f"Content: {post.selftext}"
                else:
                    post_content += "Content: [Link post - no text content]"
                
                # Add metadata
                post_content += f"\n\nUpvotes: {post.score}"
                post_content += f"\nComments: {post.num_comments}"
                post_content += f"\nURL: {post.url}"
                
                # Scrape comments if enabled
                if include_comments and post.num_comments > 0:
                    try:
                        logger.debug(f"Scraping comments for post: {post.title[:50]}...")
                        comments_content = scrape_post_comments(post, max_comments)
                        if comments_content:
                            post_content += f"\n\n--- COMMENTS ---\n{comments_content}"
                    except Exception as e:
                        logger.warning(f"Error scraping comments for post {post.id}: {e}")
                
                raw_content.append(post_content)
                posts_processed += 1
                
                logger.debug(f"Scraped post with comments: {post.title[:50]}...")
                
                # Rate limiting - be respectful to Reddit's API
                time.sleep(Config.REQUEST_DELAY)
                
            except Exception as e:
                logger.warning(f"Error processing post {post.id}: {e}")
                continue
        
        logger.info(f"Successfully scraped {posts_processed} posts from r/ppc")
        return raw_content
        
    except Exception as e:
        logger.error(f"Error scraping r/ppc: {e}")
        return []

def scrape_post_comments(submission, max_comments=10, max_depth=2):
    """
    Scrape comments from a specific Reddit post submission.
    
    Args:
        submission: PRAW submission object
        max_comments (int): Maximum number of comments to scrape
        max_depth (int): Maximum comment thread depth to scrape
    
    Returns:
        str: Formatted comments text
    """
    try:
        comments_text = []
        comments_scraped = 0
        
        # Expand comments (limit to avoid too much data)
        submission.comments.replace_more(limit=3)
        
        def extract_comments(comment_list, depth=0):
            nonlocal comments_scraped
            
            if depth > max_depth or comments_scraped >= max_comments:
                return
            
            for comment in comment_list:
                if comments_scraped >= max_comments:
                    break
                    
                try:
                    if hasattr(comment, 'body') and comment.body != '[deleted]' and comment.body != '[removed]':
                        # Format comment with depth indication
                        indent = "  " * depth
                        comment_text = f"{indent}Comment: {comment.body}"
                        
                        # Add comment metadata
                        if hasattr(comment, 'score'):
                            comment_text += f" (Score: {comment.score})"
                        
                        comments_text.append(comment_text)
                        comments_scraped += 1
                        
                        # Recursively get replies if within depth limit
                        if hasattr(comment, 'replies') and depth < max_depth and comments_scraped < max_comments:
                            extract_comments(comment.replies, depth + 1)
                            
                except Exception as e:
                    logger.debug(f"Error processing comment: {e}")
                    continue
        
        # Start extracting comments
        extract_comments(submission.comments)
        
        if comments_text:
            return '\n'.join(comments_text)
        else:
            return ""
            
    except Exception as e:
        logger.warning(f"Error extracting comments: {e}")
        return ""

def scrape_reddit_posts(subreddits, keywords=None, limit=100):
    """
    Scrape Reddit posts from specified subreddits.
    
    Args:
        subreddits (list): List of subreddit names to scrape
        keywords (list): Optional keywords to filter posts
        limit (int): Maximum number of posts to scrape
    
    Returns:
        list: Raw text content from Reddit posts
    """
    try:
        reddit = get_reddit_client()
        raw_content = []
        
        for subreddit_name in subreddits:
            try:
                logger.info(f"Scraping r/{subreddit_name}")
                subreddit = reddit.subreddit(subreddit_name)
                
                posts_per_subreddit = limit // len(subreddits)
                posts = subreddit.hot(limit=posts_per_subreddit)
                
                for post in posts:
                    try:
                        # Skip stickied posts
                        if post.stickied:
                            continue
                        
                        # Filter by keywords if provided
                        if keywords:
                            post_text = f"{post.title} {post.selftext}".lower()
                            if not any(keyword.lower() in post_text for keyword in keywords):
                                continue
                        
                        # Combine title and content
                        post_content = f"Title: {post.title}\n\n"
                        if post.selftext:
                            post_content += f"Content: {post.selftext}"
                        
                        raw_content.append(post_content)
                        
                        # Rate limiting
                        time.sleep(Config.REQUEST_DELAY)
                        
                    except Exception as e:
                        logger.warning(f"Error processing post: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error scraping r/{subreddit_name}: {e}")
                continue
        
        logger.info(f"Scraped {len(raw_content)} posts from {len(subreddits)} subreddits")
        return raw_content
        
    except Exception as e:
        logger.error(f"Error in scrape_reddit_posts: {e}")
        return []

def scrape_reddit_comments(post_url, max_depth=3):
    """
    Scrape comments from a specific Reddit post.
    
    Args:
        post_url (str): URL of the Reddit post
        max_depth (int): Maximum comment thread depth to scrape
    
    Returns:
        list: Raw comment text content
    """
    try:
        reddit = get_reddit_client()
        
        # Extract post ID from URL
        post_id = post_url.split('/')[-3] if '/comments/' in post_url else post_url.split('/')[-1]
        submission = reddit.submission(id=post_id)
        
        logger.info(f"Scraping comments from post: {submission.title[:50]}...")
        
        raw_comments = []
        
        # Expand all comments
        submission.comments.replace_more(limit=0)
        
        def extract_comments(comment_list, depth=0):
            if depth > max_depth:
                return
            
            for comment in comment_list:
                try:
                    if hasattr(comment, 'body') and comment.body != '[deleted]':
                        comment_text = f"Comment (depth {depth}): {comment.body}"
                        comment_text += f"\nUpvotes: {comment.score}"
                        raw_comments.append(comment_text)
                        
                        # Recursively get replies
                        if hasattr(comment, 'replies') and depth < max_depth:
                            extract_comments(comment.replies, depth + 1)
                            
                except Exception as e:
                    logger.warning(f"Error processing comment: {e}")
                    continue
        
        extract_comments(submission.comments)
        
        logger.info(f"Scraped {len(raw_comments)} comments from post")
        return raw_comments
        
    except Exception as e:
        logger.error(f"Error scraping comments from {post_url}: {e}")
        return []

def test_reddit_connection():
    """
    Test Reddit API connection and credentials.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        reddit = get_reddit_client()
        user = reddit.user.me()
        logger.info(f"Reddit connection test successful. Authenticated as: {user}")
        return True
        
    except Exception as e:
        logger.error(f"Reddit connection test failed: {e}")
        return False