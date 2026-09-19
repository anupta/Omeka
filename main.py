from fastmcp import FastMCP
import requests
import configparser
import sys

omeka_items_url = ""
omeka_site_url = ""
omeka_api_key_identity = ""
omeka_api_key_credential = ""

mcp = FastMCP("Omeka MCP")

def parse_conf(path: str = "config.ini"):
    config = configparser.ConfigParser()
    config.read(path)
    global omeka_items_url, omeka_site_url, omeka_api_key_identity, omeka_api_key_credential
    if 'omeka' in config:
        section = config['omeka']
        omeka_items_url = section.get('items_url', '').rstrip('/')
        omeka_site_url = section.get('site_url', '').rstrip('/')
        omeka_api_key_identity = section.get('api_key_identity', '')
        omeka_api_key_credential = section.get('api_key_credential', '')

def format_value(value) -> str:
    if isinstance(value, dict):
        simple_value = value.get('@value') or value.get('display_title') or value.get('o:id') or value.get('id')
        if simple_value is not None:
            return str(simple_value)
        return "; ".join(
            f"{key}: {nested_value}" for key, nested_value in value.items() if key != '@id'
        ) or "[linked resource]"
    return str(value)

def format_item(item: dict) -> str:
    """Format an Omeka item and its metadata for an MCP response."""
    output = []
    item_id = item.get('o:id', 'N/A')
    if omeka_site_url and item_id != 'N/A':
        site_url = omeka_site_url.rstrip('/')
        item_url = f"{site_url}/{item_id}" if site_url.endswith('/item') else f"{site_url}/item/{item_id}"
    else:
        item_url = item.get('@id', 'N/A')
    output.append(f"ID: {item_id}")
    output.append(f"Public item page: {item_url}")
    output.append(f"Title: {item.get('o:title', 'N/A')}")
    for key, values in item.items():
        if key.startswith('@') or key in {'o:id', 'o:title'} or not isinstance(values, list):
            continue
        formatted_values = [format_value(value) for value in values]
        if formatted_values:
            output.append(f"{key}: {'; '.join(formatted_values)}")
    return "\n".join(output)

def request_params() -> dict:
    params = {}
    if omeka_api_key_identity and omeka_api_key_credential:
        params.update({
            'key_identity': omeka_api_key_identity,
            'key_credential': omeka_api_key_credential,
        })
    return params

def safe_omeka_search(query: str, page: int = 1, limit: int = 10) -> list:
    try:
        if not omeka_items_url:
            return ["Omeka items_url is not configured."]
        params = request_params()
        if query:
            params['search'] = query
        params.update({'page': max(page, 1), 'per_page': min(max(limit, 1), 100)})
        response = requests.get(omeka_items_url, params=params, timeout=10)
        response.encoding = 'utf-8'

        if not response.ok:
            return [f"Error {response.status_code}: {response.text.strip()}"]

        items = response.json()
        results = [format_item(item) + "\n" + "-" * 40 for item in items]

        return results if results else ["No results found."]
    except Exception as e:
        return [f"Request failed: {str(e)}"]

def safe_omeka_get_item(item_id: int) -> list:
    try:
        if not omeka_items_url:
            return ["Omeka items_url is not configured."]
        response = requests.get(f"{omeka_items_url}/{item_id}", params=request_params(), timeout=10)
        response.encoding = 'utf-8'
        if not response.ok:
            return [f"Error {response.status_code}: {response.text.strip()}"]
        return [format_item(response.json())]
    except Exception as e:
        return [f"Request failed: {str(e)}"]

@mcp.tool()
def search_items(query: str = "", page: int = 1, limit: int = 10) -> list:
    """Search Omeka items and return their metadata."""
    return safe_omeka_search(query, page, limit)

@mcp.tool()
def get_item(item_id: int) -> list:
    """Fetch one Omeka item by its numeric ID."""
    return safe_omeka_get_item(item_id)

if __name__ == "__main__":
    parse_conf(sys.argv[1] if len(sys.argv) == 2 else "config.ini")
    mcp.run()
