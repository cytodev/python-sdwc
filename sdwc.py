import json
import os
import requests
import sys
import wget
import urllib.error

sorting = "top"
subreddit = "r/earthporn"
orientation = "landscape"
imagesToGrab = 7
minResolution = {"width": 1920, "height": 1080}

def main(imagesToGrab):
    version = "v1.0.0"
    baseURL = "https://www.reddit.com/"

    response = requests.get(baseURL + subreddit + "/" + sorting + "/.json?limit=100", headers = {"User-agent": "subreddit desktop wallpaper crawler " + version})
    jsondata = json.loads(response.text)

    if "error" in jsondata:
        sys.stdout.write(jsondata["message"] + "\n")

    if "data" not in jsondata:
        sys.stdout.write("Invalid data received: " + jsondata + "\n")

        return

    cleanOutputDirectory()

    if "children" not in jsondata["data"]:
        sys.stdout.write("No posts found on " + baseURL + subreddit + ".\n")

        return

    imagesGrabbed = 0

    for item in jsondata["data"]["children"]:
        postURL = "Post"

        if imagesGrabbed == imagesToGrab:
            return

        if "data" not in item:
            sys.stdout.write("Subreddit contains no data.\n")

            continue

        if "id" in item["data"]:
            postURL = baseURL + subreddit + "/comments/" + item["data"]["id"]

        if "preview" not in item["data"]:
            sys.stdout.write(postURL + " contains no preview.\n")

            continue

        if "images" not in item["data"]["preview"]:
            sys.stdout.write(postURL + " contains no images.\n")

            continue

        for image in item["data"]["preview"]["images"]:
            if "source" not in image:
                sys.stdout.write(postURL + " has no image source.\n")

                continue

            if "url" not in image["source"]:
                sys.stdout.write(postURL + " has no image URL.\n")

                continue

            if "height" not in image["source"] or "width" not in image["source"]:
                sys.stdout.write(postURL + " image does not have any dimension data.\n")

                continue

            if checkImageDimensions(image["source"]["height"], image["source"]["width"]):
                if downloadImage(image["source"]["url"]):
                    imagesGrabbed += 1
            else:
                sys.stdout.write(postURL + " image does not meet dimension requirements.\n")
        pass
    pass

    return

def cleanOutputDirectory():
    for dirpath, dirnames, filenames in os.walk("./output"):
        for name in filenames:
            path = os.path.join(dirpath, name)

            if path != "./output/.gitkeep":
                os.unlink(path)

    return

def checkImageDimensions(height, width):
    if orientation == "landscape" and height > width:
        return False

    if orientation == "portrait" and height < width:
        return False

    if minResolution["height"] > height or minResolution["width"] > width:
        return False

    return True

def downloadImage(url):
    url = url.split("?")[0]
    fileName = url.split("/")[-1]

    if "preview.redd.it" in url:
        url = "https://i.redd.it/" + fileName

    try:
        wget.download(url, "./output/" + fileName, wget.bar_thermometer)
        sys.stdout.write("\n")

        return True
    except urllib.error.HTTPError as httpError:
        sys.stdout.write("Unable to download image from \"" + url + "\". " + str(httpError.code) + ": " + httpError.reason + "\n")
    except ValueError as valueError:
        sys.stdout.write(str(valueError) + "\033[m\n")

    return False

main(imagesToGrab)
