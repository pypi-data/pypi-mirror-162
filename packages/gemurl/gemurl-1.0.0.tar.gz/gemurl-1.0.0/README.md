# gemurl

A library for normalizing gemini:// URLs

## Usage

The package can be installed from PyPI using pip:

    $ pip install gemurl

Use it like this:

    from gemurl import normalize_url

    print(normalize_url("GEMINI://EXAMPLE.COM:1965"))
    # Should print: gemini://example.com/

The package also includes a command like tool:

    $ gemurl normalize GEMINI://EXAMPLE.COM:1965
    gemini://example.com/

## API

* `gemurl.normalize_url(url: str) -> str` - Normalize a URL according to RFC 3986 and the Gemini specification
* `gemurl.host_port_pair_from_url(url: str) -> tuple[str, int]` - Get a (host, port) tuple suitable for connecting a socket

## Features

The normamlization function ensures that:

* Scheme and host case are always lowercase.
* The host is IDNA-encoded, if it has non-ASCII characters.
* The port is removed if it has the default 1965 value.
* Percent encoding hex digit are always uppercase.
* Non-reserved characters are never percent encoded.
* Non-printable (and non-ASCII) characters are always percent encoded.
* Percent encoding of reserved characters are not changed (since that would change the meaning).
* URLs with no paths get a single slash path.
* . and .. path segments are collapsed.
* Empty queries and fragments are distinct from missing ones.
* See test cases in `test_url.py` in te source code for the full list.


## Ideas for Future Improvements

* Function to resolve relative URLs
* Function to find the "capsule prefix" (host and port, but also /~user part if present)
* Function to convert URLs to display form (decode percent and IDNA encoding)