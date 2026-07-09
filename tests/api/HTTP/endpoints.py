from dataclasses import dataclass
import xml.etree.ElementTree as ET # for parsing XML body
from enum import Enum
from typing import Dict, Optional
import json
from pathlib import Path


# --- body parsers: each raises/asserts if the body isn't what it claims ---
def _parse_json(response):
    response.json()                       # raises ValueError if not valid JSON

def _parse_xml(response):
    ET.fromstring(response.text)          # raises ParseError if not well-formed XML

def _parse_text(response):                # raises assertion error if text is empty. not much parsing to do on text TODO: decide. maybe empty text return is fine. check later
    assert response.text != "", "expected a non-empty text body"

class ContentType(Enum):
    """The kinds of body an endpoint can return.
    Each entry has the header string to check the Content-Type and
    a reference to which function is used to check whether its a valid json/xml"""
    #      (header string,              body parser)    #TODO: we ever use xml or text?
    JSON = ("application/json",         _parse_json)
    FHIR = ("application/fhir+json",    _parse_json)   
    XML  = ("application/xml",          _parse_xml)
    TEXT = ("text/plain",               _parse_text)
    FORM = ("application/x-www-form-urlencoded",    None)#TODO: add parser
    SKIP = (None,                       None)           #if you'd like to skip validation for this endpoint

    #   name the header string and body parser so you can access them with:
    #   - {object}.header_match
    #   - {object}.parser
    def __init__(self, header_match, parser):
        self.header_match = header_match
        self.parser = parser


@dataclass(frozen=True)
class Endpoint:
    """class with the minimal info about an endpoint needed for the basic tests"""
    path: str                               #TODO: figure out whether to make seperate places for /rmh-**-01/ bc this creates long endpoints
    method: str = "GET"                     #Default since most tests are GET. set "method":"POST" when needed
    auth: bool = True                       #True if the endpoint requires credentials
    content: ContentType = ContentType.JSON #set the contentType to check the Content-Type header
    headers: Optional[Dict[str, str]] = None#optionally add headers
    params: Optional[Dict[str, str]] = None #optionally add params
    body_file: str = None                   #path to the body that you'd like to use.
    body_content: ContentType = ContentType.FHIR #TODO: are all api posts FHIR?


def load_endpoints(path: str) -> list[Endpoint]:
    with open(path) as f:
        raw = json.load(f)

    endpoints = []
    for entry in raw:
        entry = dict(entry)  # copy, don't mutate
        if "content" in entry:
            entry["content"] = ContentType[entry["content"]]
        if "body_content" in entry:
            entry["body_content"] = ContentType[entry["body_content"]]
        endpoints.append(Endpoint(**entry))
    return endpoints


#Add endpoints to be tested here. 
#Format:    Endpoint class -> see class in endpoint.definitions
#           "path" -> url to the api. path="pathhere"
#           "method" -> defaults to GET, change if needed. method="POST"
#           "auth" -> true if this endpoint should authenticate. False if it should have no auth. default to True. auth=False
#           "content" -> set which Content-Type header and body you're expecting. For types check endpoint.definitions ContentType. defaults to JSON. content=ContentType.{??}
#           "Params" -> optionally add your params here. params={"key":"value"}
#           "headers" -> optionally add your headers here. headers={"key":"value"}

ENDPOINTS = load_endpoints(str(Path(__file__).parent / "endpoints.json"))