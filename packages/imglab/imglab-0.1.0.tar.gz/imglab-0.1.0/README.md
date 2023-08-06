# imglab

`imglab` is the official Python package to integrate with imglab services.

## Installation

```sh
$ pip install imglab
```

## Python compatibility

`imglab` has been successfully tested with the following Python versions: `3.10`, `3.9`, `3.8`, `3.7`, `3.6`.

## Generating URLs

You can use `imglab.url` function to generate imglab compatible URLs for your application.

The easiest way to generate a URL is to specify the name of the `source`, a `path` and required `parameters`:

```python
>>> import imglab
>>> imglab.url("assets", "image.jpeg", width=500, height=600)
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600'

>>> imglab.url("avatars", "user-01.jpeg", width=300, height=300, mode="crop", crop="face", format="webp")
'https://avatars.imglab-cdn.net/user-01.jpeg?width=300&height=300&mode=crop&crop=face&format=webp'

```

If some specific settings are required for the source you can use an instance of `imglab.Source` class instead:

```python
>>> imglab.url(imglab.Source("assets"), "image.jpeg", width=500, height=600)
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600'

```

### Using secure image sources

For sources that require signed URLs you can specify `secure_key` and `secure_salt` attributes:

```python
>>> source = imglab.Source("assets", secure_key="55IX1RVlDHpgl/4D", secure_salt="ITvYA2lPfyz0w8/v")
>>> imglab.url(source, "image.jpeg", width=500, height=600)
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&signature=16sKGTU_dgMVqzU1JUBfkkmUV3vCKoZFkwVBYiqnGZU'

```

`signature` query parameter will be automatically generated and attached to the returned URL.

> Note: `secure_key` and `secure_salt` attributes are secrets that should not be added to a code repository. Please use environment vars or other secure method to use them in your application.

### Using HTTP instead of HTTPS

In the case that HTTP schema is required instead of HTTPS you can set `https` attribute to `False` when creating the source:

```python
>>> imglab.url(imglab.Source("assets", https=False), "image.jpeg", width=500, height=600)
'http://assets.imglab-cdn.net/image.jpeg?width=500&height=600'

```

> Note: HTTPS is the default and recommended way to generate URLs with imglab.

### Specifying parameters

Any parameter from the imglab API can be used to generate URLs with `imglab.url` method. For parameters that required dashes characters like `trim-color` you can use regular underscore argument names like `trim_color` those will be normalized in the URL generation to it's correct form:

```python
>>> imglab.url("assets", "image.jpeg", trim="color", trim_color="black")
'https://assets.imglab-cdn.net/image.jpeg?trim=color&trim-color=black'

```

If necessary you can pass a dictionary instead of a list of keyword arguments, unpacking the dictionary with `**` operator:

```python
>>> imglab.url("assets", "image.jpeg", **{"trim": "color", "trim-color": "black"})
'https://assets.imglab-cdn.net/image.jpeg?trim=color&trim-color=black'

```

### Specifying color parameters

Some imglab parameters can receive a color as value. It is possible to specify these color values as strings:

```python
>>> # Specifying a RGB color as string
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color="255,0,0")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=255%2C0%2C0'

>>> # Specifying a RGBA color as string
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color="255,0,0,128")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=255%2C0%2C0%2C128'

>>> # Specifying a named color as string
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color="red")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=red'

>>> # Specifying a hexadecimal color as string
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color="F00")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=F00'

```

You can additionally use `imglab.color` helper to specify color values:

```python
>>> from imglab import color

>>> # Using color helper function for a RGB color
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color=color(255, 0, 0))
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=255%2C0%2C0'

>>> # Using color helper function for a RGBA color
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color=color(255, 0, 0, 128))
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=255%2C0%2C0%2C128'

>>> # Using color helper function for a named color
>>> imglab.url("assets", "image.jpeg", width=500, height=600, mode="contain", background_color=color("red"))
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&mode=contain&background-color=red'

```

> Note: specify hexadecimal color values using `imglab.color` helper function is not allowed. You can use strings instead.

### Specifying position parameters

Some imglab parameters can receive a position as value. It is possible to specify these values using strings:

```python
>>> # Specifying a horizontal and vertical position as string
>>> imglab.url("assets", "image.jpeg", width=500, height=500, mode="crop", crop="left,top")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=500&mode=crop&crop=left%2Ctop'

>>> # Specifying a vertical and horizontal position as string
>>> imglab.url("assets", "image.jpeg", width=500, height=500, mode="crop", crop="top,left")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=500&mode=crop&crop=top%2Cleft'

>>> # Specifying a position as string
>>> imglab.url("assets", "image.jpeg", width=500, height=500, mode="crop", crop="left")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=500&mode=crop&crop=left'

```

You can additionally use `imglab.position` helper function to specify position values:

```python
>>> from imglab import position

>>> # Using position function helper for a horizontal and vertical position
>>> imglab.url("assets", "image.jpeg", width=500, height=500, mode="crop", crop=position("left", "top"))
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=500&mode=crop&crop=left%2Ctop'

>>> # Using position function helper for a vertical and horizontal position
>>> imglab.url("assets", "image.jpeg", width=500, height=500, mode="crop", crop=position("top", "left"))
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=500&mode=crop&crop=top%2Cleft'

>>> # Using position function helper for a single position
>>> imglab.url("assets", "image.jpeg", width=500, height=500, mode="crop", crop=position("left"))
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=500&mode=crop&crop=left'

```

### Specifying URL parameters

Some imglab parameters can receive URLs as values. It is possible to specify these parameter values as strings:

```python
>>> imglab.url("assets", "image.jpeg", width=500, height=600, watermark="logo.svg")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&watermark=logo.svg'

```

And even use parameters if required:

```python
>>> imglab.url("assets", "image.jpeg", width=500, height=600, watermark="logo.svg?width=100&format=png")
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&watermark=logo.svg%3Fwidth%3D100%26format%3Dpng'

```

Additionally you can use nested `imglab.url` calls to specify these URL values:

```python
>>> imglab.url(
...     "assets",
...     "image.jpeg",
...     width=500,
...     height=600,
...     watermark=imglab.url("assets", "logo.svg", width=100, format="png")
... )
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&watermark=https%3A%2F%2Fassets.imglab-cdn.net%2Flogo.svg%3Fwidth%3D100%26format%3Dpng'

```

If the resource is located in a different source we can specify it using `imglab.url`:

```python
>>> imglab.url(
...     "assets",
...     "image.jpeg",
...     width=500,
...     height=600,
...     watermark=imglab.url("marketing", "logo.svg", width=100, format="png")
... )
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&watermark=https%3A%2F%2Fmarketing.imglab-cdn.net%2Flogo.svg%3Fwidth%3D100%26format%3Dpng'

```

Using secure sources for URLs parameter values is possible too:

```python
>>> marketing = imglab.Source("marketing", secure_key="55IX1RVlDHpgl/4D", secure_salt="ITvYA2lPfyz0w8/v")
>>> imglab.url(
...     "assets",
...     "image.jpeg",
...     width=500,
...     height=600,
...     watermark=imglab.url(marketing, "logo.svg", width=100, format="png")
... )
'https://assets.imglab-cdn.net/image.jpeg?width=500&height=600&watermark=https%3A%2F%2Fmarketing.imglab-cdn.net%2Flogo.svg%3Fwidth%3D100%26format%3Dpng%26signature%3DMd4V23DOkn5hHw_nAjkEG9lKHOZ8wjDBmYi2d5TCaCc'

```

`signature` query parameter will be automatically generated and attached to the nested URL value.

### Specifying URLs with expiration timestamp

The `expires` parameter allows you to specify a UNIX timestamp in seconds after which the request is expired.

If a `datetime` or `struct_time` instance is specified as value to `expires` parameter it will be automatically converted to UNIX timestamp. In the following example, we specify an expiration time of one hour:

```python
import datetime
expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
imglab.url("assets", "image.jpeg", width=500, expires=expires_at)
```

> Note: The `expires` parameter should be used in conjunction with secure sources. Otherwise, `expires` value could be tampered with.

## Generating URLs for on-premises imglab server

For on-premises imglab server is possible to define custom sources pointing to your server location.

* `https` - a `boolean` value specifying if the source should use https or not (default: `True`)
* `host` - a `string` specifying the host where the imglab server is located. (default: `"imglab-cdn.net"`)
* `port` - an `integer` specifying a port where the imglab server is located. (default: `None`)
* `subdomains` - a `bool` value specifying if the source should be specified using subdomains instead of using the path. (default: `True`)

If we have our on-premises imglab server at `http://my-company.com:8080` with a source named `images` we can use the following source settings to access a `logo.png` image:

```python
>>> source = imglab.Source("images", https=False, host="my-company.com", port=8080)
>>> imglab.url(source, "logo.png", width=300, height=300, format="png")
'http://images.my-company.com:8080/logo.png?width=300&height=300&format=png'

```

It is possible to use secure sources too:

```python
>>> source = imglab.Source(
...     "images",
...     https=False,
...     host="my-company.com",
...     port=8080,
...     secure_key="55IX1RVlDHpgl/4D",
...     secure_salt="ITvYA2lPfyz0w8/v"
... )
>>> imglab.url(source, "logo.png", width=300, height=300, format="png")
'http://images.my-company.com:8080/logo.png?width=300&height=300&format=png&signature=spnbiXwImfp6PpihAqVJenm0IGdC-h5inIhViYp4_TU'

```

### Using sources with disabled subdomains

In the case that your on-premises imglab server is configured to use source names as paths instead of subdomains you can set `subdomains` attribute to `False`:

```python
>>> source = imglab.Source(
...     "images",
...     https=False,
...     host="my-company.com",
...     port=8080,
...     subdomains=False
... )
>>> imglab.url(source, "logo.png", width=300, height=300, format="png")
'http://my-company.com:8080/images/logo.png?width=300&height=300&format=png'

```

## License

imglab source code is released under [MIT License](LICENSE).
