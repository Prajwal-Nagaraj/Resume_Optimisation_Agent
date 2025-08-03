from jobspy import scrape_jobs
from datetime import datetime, timedelta

class SpeedyApplyTool:
    """A tool to find job listings and return them as a DataFrame."""

    def find_and_save_jobs(self, search_term: str, location: str, time_days: int = 4, proxy_url: str = None):
        """Scrapes job listings for a given search term and location, 
        and returns the DataFrame directly.

        Args:
            search_term: The job title or keywords to search for.
            location: The location to search for jobs in.
            time_days: Number of days old the jobs should be (default: 4 days).
            proxy_url: Optional proxy URL to use instead of the default proxy list.

        Returns:
            The DataFrame containing job listings if successful, otherwise None.
        """
        # Calculate the date based on the time_days parameter
        date_ago = datetime.now() - timedelta(days=time_days)
        formatted_date = date_ago.strftime("%d %b %Y")

        google_search_query = f"{search_term} jobs near {location} since {formatted_date}"

        try:
            # Use provided proxy or fall back to proxy list
            proxies_to_use = [proxy_url] if proxy_url else None
            
            jobs_df = scrape_jobs(
                site_name=["linkedin"],
                search_term=search_term,
                google_search_term=google_search_query,
                location=location,
                results_wanted=20,
                hours_old=time_days * 24,  # Convert days to hours
                linkedin_fetch_description=True,
                proxies=proxies_to_use
            )
        except Exception as e:
            print(f"Error during job scraping: {e}")
            return None
        
        if jobs_df is not None and not jobs_df.empty:
            print(f"Found {len(jobs_df)} jobs.")
            return jobs_df
        else:
            print("No jobs found or an error occurred during scraping.")
            return None

if __name__ == "__main__":
    # Example usage of the SpeedyApplyTool:
    tool = SpeedyApplyTool()
    
    search_query = "AI Product Manager"
    job_location = "New York, USA"
    time_days = 7  # Search for jobs posted in the last 7 days
    
    jobs_df = tool.find_and_save_jobs(search_term=search_query, location=job_location, time_days=time_days, proxy_url="https://spm7e96ly4:Pl=r66vUAut2asdwE0@gate.decodo.com:10001")
    
    if jobs_df is not None and not jobs_df.empty:
        print(f"Process completed. Found {len(jobs_df)} jobs.")
        print("Sample job data:")
        print(jobs_df.head())
    else:
        print("Process completed. No job data was found.")