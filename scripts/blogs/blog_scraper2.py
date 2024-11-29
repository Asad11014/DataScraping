import os
import time
import requests
from bs4 import BeautifulSoup
from weasyprint import HTML


def scrape_all_blog_posts(base_url, max_posts=None):
    """
    Scrape all blog posts from the website, navigating through pages using 'Older Posts' links.

    Args:
        base_url (str): Base URL of the blog.
        max_posts (int, optional): Maximum number of posts to scrape. Default is None (scrape all posts).

    Returns:
        list: List of dictionaries containing post titles, HTML content, and URLs.
    """
    blog_posts = []
    next_page_url = base_url  # Start with the base URL
    post_counter = 0  # Initialize a counter to track the number of posts scraped

    try:
        while next_page_url:
            # Send a GET request to the current page
            try:
                response = requests.get(next_page_url, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error fetching page {next_page_url}: {e}")
                break

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Scrape posts on the current page
            post_links = soup.find_all('h3', class_='post-title entry-title')

            if not post_links:
                print(f"No posts found on page {next_page_url}. Exiting...")
                break

            for post in post_links:
                # Extract the post URL
                post_url = post.find('a').get('href')
                try:
                    post_response = requests.get(post_url, timeout=10)
                    post_response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Error fetching post {post_url}: {e}")
                    continue

                post_soup = BeautifulSoup(post_response.text, 'html.parser')

                # Extract title
                title = post_soup.find('h3', class_='post-title entry-title').get_text(strip=True)

                # Extract content (HTML format)
                content_div = post_soup.find('div', class_='post-body entry-content')
                content_html = str(content_div) if content_div else "<p>No content found</p>"

                # Add the post details to the list
                blog_posts.append({
                    'title': title,
                    'content_html': content_html,
                    'url': post_url
                })

                # Increment counter and log progress
                post_counter += 1
                print(f"Scraped {post_counter} posts so far...")

                # Stop if we've reached the max_posts limit
                if max_posts and post_counter >= max_posts:
                    print(f"Reached max posts limit of {max_posts}. Stopping...")
                    return blog_posts

            # Break the loop if no more pages are available or max_posts is reached
            if max_posts and post_counter >= max_posts:
                break

            # Find the 'Older Posts' link to navigate to the next page
            older_posts_link = soup.find('a', id='Blog1_blog-pager-older-link')
            if older_posts_link:
                next_page_url = older_posts_link.get('href')
            else:
                next_page_url = None  # No more pages to scrape

    except Exception as e:
        print(f"Unexpected error: {e}")

    print(f"Scraping complete. Total posts scraped: {post_counter}")
    return blog_posts



def save_to_pdf_with_formatting(blog_posts, filename='all_blog_posts2.pdf'):
    """
    Save blog posts to a PDF file, preserving HTML formatting and images.

    Args:
        blog_posts (list): List of blog post dictionaries.
        filename (str): Output PDF filename.
    """
    try:
        print("Starting to generate HTML content for the PDF...")

        start_time = time.time()
        
        # Create HTML content for all posts
        html_content = '<html><body>'
        for i, post in enumerate(blog_posts, start=1):
            html_content += f"<h1>{post['title']}</h1>"
            html_content += f"<p><a href='{post['url']}'>Original Post URL</a></p>"
            html_content += post['content_html']
            html_content += '<hr>'  # Separator between posts
            print(f"Added post {i}/{len(blog_posts)} to the HTML content.")

        html_content += '</body></html>'

        html_generation_time = time.time() - start_time  # Time taken for HTML generation
        print(f"HTML content generation complete. Time taken: {html_generation_time:.2f} seconds.")

        # Convert the HTML content to a PDF
        print(f"Starting PDF generation with WeasyPrint. Output file: {filename}")

        start_time = time.time()
        HTML(string=html_content).write_pdf(filename)
        pdf_generation_time = time.time() - start_time
        print(f"PDF generation complete. Time taken: {pdf_generation_time:.2f} seconds.")

    except Exception as e:
        print(f"Error saving to PDF: {e}")

    """
    Save blog posts to a PDF file, preserving HTML formatting and images.

    Args:
        blog_posts (list): List of blog post dictionaries.
        filename (str): Output PDF filename.
    """
    try:
        # Create HTML content for all posts
        html_content = '<html><body>'
        for post in blog_posts:
            html_content += f"<h1>{post['title']}</h1>"
            html_content += f"<p><a href='{post['url']}'>Original Post URL</a></p>"
            html_content += post['content_html']
            html_content += '<hr>'  # Separator between posts
        html_content += '</body></html>'

        options = {
            'zoom': 0.8,
            'enable_javascript': False,
        }

        # Convert the HTML content to a PDF
        HTML(string=html_content).write_pdf(filename)
        print(f"Blog posts saved to {filename}")

    except Exception as e:
        print(f"Error saving to PDF: {e}")


def main():
    # Base URL of the blog
    base_url = 'http://blog.theswca.com'

    # Limit posts
    max_posts = 30

    # Scrape all blog posts
    blog_posts = scrape_all_blog_posts(base_url, max_posts=max_posts)

    if not blog_posts:
        print("No blog posts found.")
        return

    # Save to PDF with formatting
    save_to_pdf_with_formatting(blog_posts)


if __name__ == '__main__':
    main()
