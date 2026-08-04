# -*- coding: utf-8 -*-

import re
import base64
from resources.lib import utils


def Tdecode(vidurl):
    replacemap = {
        "M": "\u041c",
        "A": "\u0410",
        "B": "\u0412",
        "C": "\u0421",
        "E": "\u0415",
        "=": "~",
        "+": ".",
        "/": ",",
    }

    for key, val in replacemap.items():
        vidurl = vidurl.replace(val, key)
        # Handle case where raw backslash escape string r"\u0415" is passed
        raw_val = r"\u" + f"{ord(val[0]):04x}" if len(val) == 1 and ord(val[0]) > 128 else None
        if raw_val:
            vidurl = vidurl.replace(raw_val, key)

    vidurl = base64.b64decode(vidurl)
    return vidurl.decode("utf-8")


def GetTxxxVideo(vidpage):
    vidpagecontent = utils.getHtml(vidpage)
    posturl = "https://%s/sn4diyux.php" % vidpage.split("/")[2]

    pC3 = re.search("""pC3:'([^']+)""", vidpagecontent).group(1)
    vidid = re.search(r"""video_id["|']?:\s*(\d+)""", vidpagecontent).group(1)
    data = "%s,%s" % (vidid, pC3)
    vidcontent = utils.getHtml(posturl, referer=vidpage, data={"param": data})
    vidurl = re.search('video_url":"([^"]+)', vidcontent).group(1)
    vidurl = Tdecode(vidurl)

    return vidurl + "|Referer=" + vidpage
