import requests as rq
import xmltodict

class Client:
    def __init__(self):
        self.__API_URL = "https://safebooru.org/index.php?page=dapi"
        self.__API_POST_URL = self.__API_URL + "&s=post&q=index"
        self.__API_COMMENT_URL = self.__API_URL + "&s=comment&q=index"

    def parse_xml(self, xml_bin):
        xml = xmltodict.parse(xml_bin, encoding="utf-8")
        if ("response" in xml):
            response = xml["response"]
            if not (response["@success"]):
                print(response["@reason"])
        return xml

    def parse_post_data(self, xml):
        xml_headers = list(xml.keys())
        if ("posts" in xml_headers): 
            xml = xml["posts"]
            xml_headers = list(xml.keys())

        # "post" is the first header instead of "posts" if
        # retrieving only one post
        if ("post" in xml_headers): 
            xml = xml["post"]
        else: return []
        
        if (not type(xml) == list):
            xml = [xml]
        return xml

    def get_posts(self, tags: str, pid: int = 0, limit: int = 1, recursion: int = 0) -> list:
        tags.strip().replace(' ', "%20")
        url = self.__API_POST_URL + f"&tags={tags}&pid={pid}&limit={limit}"
        resp = rq.get(url=url)
        print(resp)
        if (resp.ok): 
            xml_bin = resp.content
            xml = self.parse_xml(xml_bin)
            xml = self.parse_post_data(xml)
            if (xml):
                print("posts retrieved successfully")
                return xml
        print("failed to retrieve posts")
        if recursion < 6:
            print(f"retrying: {recursion+1}/6")
            return self.get_posts(tags, pid, limit, recursion+1)
        else: return None

    def get_post_by_id(self, id: str) -> dict:
        id.strip().replace(' ', "%20")
        url = self.__API_POST_URL + f"&id={id}"
        resp = rq.get(url=url)
        if (resp.ok): 
            print(f"post by id {id} retrieved successfully")
            xml_bin = resp.content
            xml = self.parse_xml(xml_bin)
            xml = self.parse_post_data(xml)
            if not (xml): return False
            return xml[0]
        else: return False

    def get_comments(self, post_id):
        url = self.__API_COMMENT_URL + f"&post_id={post_id}"
        resp = rq.get(url=url)
        if (resp.ok): 
            print("comments retrieved successfully")
            xml_bin = resp.content
            xml = self.parse_xml(xml_bin)
            if ("comments" in list(xml.keys())): xml = xml["comments"]
            if ("comment" in list(xml.keys())): xml = xml["comment"]
            else: return []
            if not (type(xml) == list): xml = [xml]
            return xml
        else: return False