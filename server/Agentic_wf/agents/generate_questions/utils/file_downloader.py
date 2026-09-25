import io
import httpx

async def _download_file(file_url: str) -> io.BytesIO:
    """Download a file asynchronously and return it as a BytesIO stream."""
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(file_url)
        response.raise_for_status()
        return io.BytesIO(response.content)