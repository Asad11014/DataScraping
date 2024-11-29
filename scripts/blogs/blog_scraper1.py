import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def scrape_all_blog_posts(base_url):
    """
    Scrape all blog posts from the website, navigating through pages using 'Older Posts' links.

    Args:
        base_url (str): Base URL of the blog.

    Returns:
        list: List of dictionaries containing post titles, contents, and URLs.
    """
    blog_posts = []
    next_page_url = base_url  # Start with the base URL
    post_counter = 0  # Initialize a counter to track the number of posts scraped

    try:
        while next_page_url:
            # Send a GET request to the current page
            response = requests.get(next_page_url)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Scrape posts on the current page
            post_links = soup.find_all('h3', class_='post-title entry-title')

            for post in post_links:
                # Extract the post URL
                post_url = post.find('a').get('href')

                # Fetch individual post
                post_response = requests.get(post_url)
                post_response.raise_for_status()
                post_soup = BeautifulSoup(post_response.text, 'html.parser')

                # Extract title
                title = post_soup.find('h3', class_='post-title entry-title').get_text(strip=True)

                # Extract content
                content_div = post_soup.find('div', class_='post-body entry-content')
                content = content_div.get_text(strip=True) if content_div else "No content found"

                # Add the post details to the list
                blog_posts.append({
                    'title': title,
                    'content': content,
                    'url': post_url
                })

                # Increment counter and log progress
                post_counter += 1
                print(f"Scraped {post_counter} posts so far...")

            # Find the 'Older Posts' link to navigate to the next page
            older_posts_link = soup.find('a', id='Blog1_blog-pager-older-link')
            if older_posts_link:
                next_page_url = older_posts_link.get('href')
            else:
                next_page_url = None  # No more pages to scrape

    except requests.RequestException as e:
        print(f"Error fetching blog posts: {e}")

    print(f"Scraping complete. Total posts scraped: {post_counter}")
    return blog_posts


def save_to_pdf(blog_posts, filename='all_blog_posts1.pdf'):
    """
    Save blog posts to a PDF file.

    Args:
        blog_posts (list): List of blog post dictionaries.
        filename (str): Output PDF filename.
    """
    try:
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)

        # Get sample stylesheet
        styles = getSampleStyleSheet()

        # List to hold PDF content
        story = []

        # Add each blog post to the PDF
        for post in blog_posts:
            # Add title
            story.append(Paragraph(post['title'], styles['Title']))

            # Add URL
            story.append(Paragraph(f"URL: {post['url']}", styles['Italic']))

            # Add content
            story.append(Paragraph(post['content'], styles['Normal']))

            # Add spacer between posts
            story.append(Spacer(1, 12))

        # Build PDF
        doc.build(story)

        print(f"Blog posts saved to {filename}")

    except Exception as e:
        print(f"Error saving to PDF: {e}")


def main():
    # Base URL of the blog
    base_url = 'http://blog.theswca.com'

    # Scrape all blog posts
    blog_posts = scrape_all_blog_posts(base_url)

    if not blog_posts:
        print("No blog posts found.")
        return

    # Save to PDF
    save_to_pdf(blog_posts)


if __name__ == '__main__':
    main()
