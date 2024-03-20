import argparse
import os
import sys
import uuid

import requests


def main():
    parser = argparse.ArgumentParser(description="Tool for downloading files from CloudVerge")

    parser.add_argument("--file-id", "-f", help="File ID in the system", metavar='UUID', required=True)
    parser.add_argument("--path", "-p", help="Path to the output file (if not set, the file will be placed to cwd)", metavar='UUID', default='')
    parser.add_argument("--url", "-b", help="HTTP base url to client-api server", default="http://localhost:5010")
    parser.add_argument("--token", "-t", help="OAuth token of your account", metavar='OAUTH', default='')
    args = parser.parse_args()

    token = args.token if args.token else os.getenv("CLOUD_VERGE_TOKEN")
    if not token:
        print("OAuth token not found, trying to download anonimously")

    url = args.url.removesuffix('/')
    headers = {
        "Authorization": "OAuth " + token
    }

    resp = requests.get(
        url + f"/files/download/{args.file_id}",
        headers=headers,
        stream=True,
        allow_redirects=True
    )
    if resp.status_code != 200:
        print(f"[{resp.status_code}] Something went wrong:", resp.json()["message"], file=sys.stderr)
        exit(1)

    path = args.path
    if not path:
        disp = resp.headers.get("Content-Disposition", "")
        if "filename=" in disp:
            path = disp.split("filename=")[-1].strip('"')
        else:
            path = (uuid.uuid4()) + '.bin'

    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=16 * 1024):
            f.write(chunk)
    print("Finished! Result path:", path)


if __name__ == '__main__':
    main()
