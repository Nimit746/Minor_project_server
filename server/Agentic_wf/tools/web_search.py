from ddgs import DDGS


async def web_search(query: str):
    """This is a tool used to search about the query on the internet and other cloud services for the better and more accurate context"""
    try:
        result = DDGS().text(
            query,
            max_results = 7,
            max_retries=3
        )
        return result
    except Exception as e:
        print(f'Error in web_search: {e}')
