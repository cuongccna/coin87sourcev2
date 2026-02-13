import trafilatura
from app.core.logger import log

class ContentEnricher:
    @staticmethod
    def enrich_news(url: str, html: str = None) -> dict:
        """
        Extract full text and main image from URL using Trafilatura.
        Returns: {'full_text': str, 'image_url': str}
        """
        try:
            downloaded = html
            if not downloaded:
                downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                return {}

            # Extract full text
            full_text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            
            # Extract Metadata (Image) works better with bare extraction sometimes or separate call
            # Trafilatura extract() returns string. To get metadata need bare_extraction
            metadata = trafilatura.bare_extraction(downloaded)
            image_url = metadata.get('image') if metadata else None

            # Fallback if image not found in metadata
            if not image_url and metadata and metadata.get('sitename'):
                 pass # Could look for favicons etc, but let's keep it simple

            return {
                "full_text": full_text,
                "image_url": image_url
            }

        except Exception as e:
            log.warning(f"Enrichment failed for {url}: {e}")
            return {}
