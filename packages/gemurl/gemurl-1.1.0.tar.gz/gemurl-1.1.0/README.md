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


## API of `gemurl` Module

The `GemurlError` is the base class for all exceptions raised by
functions in this module.


### `normalize_url(url: str) -> str`

Normalize a URL according to RFC 3986 and the Gemini
specification. Raises `NormalizarionError` if the input is not a valid
(gemini) URL. Raises `NonGeminiUrlError` (which is a subclass
of `NormalizarionError`) if the scheme is non-gemini.


### `host_port_pair_from_url(normalized_url: str) -> tuple[str, int]`

Get a (host, port) tuple suitable for connecting a socket. The input
URL must be normalized for this function to work correctly.


### `capsule_prefix(normalized_url: str) -> str`

Find the prefix of the URL that uniquely identifies its capsule. Two
URLs belong to the same capsule if the hostnames and ports match, but
if the path begins with "/~USER/" or "/users/USER/", then the USER
part needs to match too.

This definition is borrowed from khuxkm's Molniya. Thanks!


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
* Function to convert URLs to display form (decode percent and IDNA encoding)