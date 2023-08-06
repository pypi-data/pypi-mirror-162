import mimetypes
from omnitools import encodeURIComponent
# type hints
from omnitools.xtype import *


def transform(
        url,  # type: str
        *,
        is_binary=None,  # type: bool
        assemble=True  # type: bool
) -> Union[str, list]:
    """
    Description: convert `url` to one understandable by Google Translate internals
    Usage: `transform("http://example.com")`\\n`transform("http://example.com/doc.pdf", is_binary=False)`\\n`transform("https://example.com/file.zip?range=0-100", is_binary=True)`
    
    :param url: the HTTP Uniform Resource Locator
    :param is_binary: is target resource binary?
    :param assemble: to join `url` parts or not
    :return: return converted url string if `assemble` else return converted url parts
    """
    whitelist = [
        "application/json",
        "application/javascript",
        "text/css",
        "image/png",
        "text/html",
        "text/plain",
    ]
    params = url.split("?")
    type = mimetypes.guess_type(params[0])[0]
    is_binary = is_binary if is_binary is not None else (url.count("/") > 2 and type and type not in whitelist)
    api_key = "3cbab51d-6f44-4569-b131-140fd3802204"
    parts = url.split("?")[0].split("/")
    subdomain = parts[2].replace(".", "-")
    if is_binary:
        path = api_key+"/ajax"
    else:
        path = "/".join(parts[3:])
    extra = "?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=op"
    if url.startswith("http://"):
        extra += "&_x_tr_sch=http"
    if is_binary:
        extra += "&u="+encodeURIComponent(url)
        params = ""
    elif len(params) == 2:
        params = "&"+params[1]
    else:
        params = ""
    if assemble:
        return "https://{}.translate.goog/{}{}{}".format(subdomain, path, extra, params)
    else:
        return [
            "https://{}.translate.goog/".format(subdomain),
            path, extra, params
        ]




