from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import requests
import json

from view import view

white = "\u001B[39m"
green = "\u001B[32m"
yellow = "\u001B[33m"

map_file_path = "dist/map.json"

def write_to_json(map):
    with open(map_file_path, "w") as f:
        json.dump(map, f, indent=4)


def filter_resource_links(href_list):
    clean_list = []

    for i in href_list:
        if i[0:4] != "http" and i[0:1] != "/":
            continue

        if i == "/":
            continue

        if (
            i[-4:] == ".png"
            or i[-4:] == ".jpg"
            or i[-4:] == ".css"
            or i[-4:] == ".ico"
            or i[-4:] == ".svg"
        ):
            continue

        clean_list.append(i)

    return clean_list


def remove_duplicates(href_list):
    clean_list = []

    for i in href_list:
        if i not in clean_list:
            clean_list.append(i)

    return clean_list


def filter_list(href_list):
    clean_list = []

    clean_list = filter_resource_links(href_list)
    clean_list = remove_duplicates(clean_list)

    return clean_list


def create_json_url_node(url):
    return {"url": url, "children": []}


def scan_url(url):
    response = requests.get(url)
    html = response.text

    href_list = []

    for i in range(len(html)):
        if html[i : i + 6] == 'href="':
            for j in range(i + 6, len(html)):
                if html[j] == '"':
                    href_list.append(html[i + 6 : j])
                    break

    clean_list = filter_list(href_list)
    return clean_list


def scan_url_node(url_node, parent_url, depth):
    if depth <= 0:
        return url_node

    print(yellow + "Depth: " + str(depth) + white + " | " + green + "URL: " + url_node["url"]+ white)

    url = url_node["url"]
    children = url_node["children"]

    if not url.startswith("http"):
        if url.startswith("/"):
            url = parent_url + url
        else:
            url = parent_url + "/" + url

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        children_list = scan_url(url)

        for i in children_list:
            child_node = create_json_url_node(i)
            children.append(child_node)
            futures.append(executor.submit(scan_url_node, child_node, url, depth - 1))

        wait(futures, return_when=ALL_COMPLETED)

    return url_node


def scan(url, depth):
    map = [{"url": url, "children": []}]

    initial_list = scan_url(url)
    for i in initial_list:
        map[0]["children"].append(create_json_url_node(i))

    for node in map:
        scan_url_node(node, url, depth)

    write_to_json(map)

def main():
    url = input("Enter URL: ")
    depth = int(input("Enter depth: "))
    
    scan(url, depth)
    
    view()


main()
