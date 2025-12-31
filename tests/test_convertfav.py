import pytest

from resources.lib import convertfav


def test_convertfav_transforms_supported_modes():
    backup = {
        "data": [
            {"mode": 518, "name": "Streamate", "url": "u1", "img": "", "duration": "", "quality": ""},
            {"mode": 342, "name": "Txxx", "url": "a/b/c/d/e", "img": "", "duration": "", "quality": ""},
            {"mode": 282, "name": "Cam4Name", "url": "ignored", "img": "", "duration": "", "quality": ""},
        ]
    }

    converted = convertfav.convertfav(backup)

    assert converted["data"] == [
        {
            "mode": "streamate.Playvid",
            "name": "Streamate",
            "url": "Streamate$$u1",
            "img": "",
            "duration": "",
            "quality": "",
        },
        {
            "mode": "txxx.Playvid",
            "name": "Txxx",
            "url": "a/b/c/e",
            "img": "",
            "duration": "",
            "quality": "",
        },
        {
            "mode": "cam4.Playvid",
            "name": "Cam4Name",
            "url": "https://www.cam4.com/Cam4Name",
            "img": "",
            "duration": "",
            "quality": "",
        },
    ]


def test_convertfav_skips_unknown_modes():
    backup = {"data": [{"mode": 9999, "name": "Unknown", "url": "url", "img": "", "duration": "", "quality": ""}]}

    converted = convertfav.convertfav(backup)

    assert converted["data"] == []
