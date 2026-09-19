# Omeka MCP

A FastMCP server that connects AI assistants to an Omeka S collection through the Omeka REST API.

## Features

- Search Omeka items by text.
- Fetch one item by numeric ID.
- Return item metadata in a readable format.
- Return public Omeka item page links instead of API links.
- Support optional Omeka API credentials.

## Requirements

- Python 3.10 or newer
- An Omeka S REST API endpoint

## Installation

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Edit `config.ini`:

```ini
[omeka]
items_url = http://<IP_Address>/omeka/api/items
site_url = http://<IP_Address>/omeka/s/terracotta/item/
api_key_identity =
api_key_credential =
```

`items_url` is used to retrieve records. `site_url` is used to create browser-facing item links. API credentials can be left empty when the Omeka API is public.

Do not commit real API credentials to source control.

## Run

Run the MCP server with the default configuration:

```powershell
python main.py
```

To use a different configuration file:

```powershell
python main.py path\to\config.ini
```

## MCP Tools

### `search_items`

Search the Omeka collection.

Parameters:

- `query`: Search text. Defaults to an empty string.
- `page`: Page number, starting at 1. Defaults to 1.
- `limit`: Number of results, from 1 to 100. Defaults to 10.

### `get_item`

Fetch one Omeka item by its numeric ID.

Parameters:

- `item_id`: The Omeka item ID.

## Example Public Link

For item `131`, the server returns:

```text
http://94.103.163.196/omeka/s/terracotta/item/131
```

The Omeka API record itself is fetched from:

```text
http://94.103.163.196/omeka/api/items/131
```
