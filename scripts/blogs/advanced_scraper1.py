import os
import time
import requests
from bs4 import BeautifulSoup
from weasyprint import HTML


def scrape_all_posts(base_url, max_posts=None):
    """
    Scrape all posts, navigating through a list of links on each page and preserving the format and images.
    """
    all_posts = []
    next_page_url = base_url  # Start at the base URL
    post_counter = 0

    try:
        while next_page_url:
            # Request the page containing the list of links
            try:
                response = requests.get(next_page_url, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error fetching page {next_page_url}: {e}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Select links inside <li> tags
            list_links = soup.select('li a[href]')

            if not list_links:
                print(f"No links found on page {next_page_url}. Exiting...")
                break

            for link in list_links:
                # Get the post URL and navigate to it
                post_url = link.get('href')
                try:
                    post_response = requests.get(post_url, timeout=10)
                    post_response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Error fetching post {post_url}: {e}")
                    continue

                post_soup = BeautifulSoup(post_response.text, 'html.parser')

                # Extract the first two <p> tags (with images included)
                p_tags = post_soup.select('p')
                if len(p_tags) < 2:
                    print(f"Not enough <p> tags in post: {post_url}")
                    continue

                first_p_html = str(p_tags[0])  # Include the HTML and images
                second_p_html = str(p_tags[1])  # Include the HTML and images

                # Extract the title
                title_tag = post_soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else "No Title"

                # Save the post details
                all_posts.append({
                    'title': title,
                    'first_p_html': first_p_html,
                    'second_p_html': second_p_html,
                    'url': post_url
                })

                post_counter += 1
                print(f"Scraped post {post_counter}: {title}")

                # Stop if we've reached the max_posts limit
                if max_posts and post_counter >= max_posts:
                    print(f"Reached max posts limit of {max_posts}. Stopping...")
                    return all_posts

            # Find the link to the next page
            next_page_link = soup.find('a', string='[Next]')
            if next_page_link:
                next_page_url = next_page_link.get('href')
                print(f"Found next page: {next_page_url}")
            else:
                next_page_url = None  # No more pages to scrape

    except Exception as e:
        print(f"Unexpected error: {e}")

    print(f"Scraping complete. Total posts scraped: {post_counter}")
    return all_posts


def save_to_pdf_with_formatting(posts, filename='scraped_posts.pdf'):
    """
    Save scraped posts to a PDF, preserving the HTML format and images.
    """
    try:
        print("Generating HTML content for the PDF...")

        # Start generating the combined HTML
        html_content = '<html><body>'
        for i, post in enumerate(posts, start=1):
            html_content += f"<h1>{post['title']}</h1>"
            html_content += f"<p><a href='{post['url']}'>Original Post URL</a></p>"
            html_content += post['first_p_html']  # Include the raw HTML of the first <p>
            html_content += post['second_p_html']  # Include the raw HTML of the second <p>
            html_content += '<hr>'  # Add a separator between posts
            print(f"Added post {i}/{len(posts)} to the HTML content.")

        html_content += '</body></html>'

        # Convert the HTML content to a PDF
        print("Converting HTML to PDF...")
        HTML(string=html_content).write_pdf(filename)
        print(f"PDF saved as {filename}")

    except Exception as e:
        print(f"Error saving to PDF: {e}")


def main():
    # Base URL of the site
    base_url = 'https://search.freefind.com/find.html?id=5544421&map=0&page=0&ics=1'

    # Limit the number of posts to scrape
    max_posts = 130

    # Scrape posts
    posts = scrape_all_posts(base_url, max_posts=max_posts)

    if not posts:
        print("No posts scraped.")
        return

    # Save to PDF
    save_to_pdf_with_formatting(posts, filename='scraped_posts.pdf')


if __name__ == '__main__':
    main()
