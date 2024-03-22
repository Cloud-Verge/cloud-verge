import argparse
import pathlib
import os
import sys

import requests


def main():
    parser = argparse.ArgumentParser(description="Tool for uploading files to CloudVerge")

    parser.add_argument("--file", "-f", help="Path to the file", metavar='PATH', required=True)
    parser.add_argument("--url", "-b", help="HTTP base url to client-api server", default="http://localhost:5010")
    parser.add_argument("--token", "-t", help="OAuth token of your account", metavar='OAUTH', default='')
    parser.add_argument("--public", "-p", help="If set, the uploaded file will be publicly accessible", action="store_true")
    args = parser.parse_args()

    token = args.token if args.token else os.getenv("CLOUD_VERGE_TOKEN")
    if not token:
        print("Cloud Verge token not found. Either env variable \"CLOUD_VERGE_TOKEN\" or --token param must be provided", file=sys.stderr)
        exit(1)

    url = args.url.removesuffix('/')
    path = pathlib.Path(args.file)
    headers = {
        "Authorization": "OAuth " + args.token
    }

    with requests.Session() as session:
        resp = session.get(
            url + "/files/upload_link",
            json={
                "access": "PUBLIC" if args.public else "PRIVATE",
            },
            headers=headers,
        )
        if resp.status_code != 200:
            print(f"[{resp.status_code}] Something went wrong:", resp.text, file=sys.stderr)
        resp = requests.put(
            resp.json()["url"],
            files={"file": open(path, "rb")},
            headers=headers,
        )
        if resp.status_code != 200:
            print(f"[{resp.status_code}] Something went wrong:", resp.text, file=sys.stderr)
            exit(1)
        resp = resp.json()

    print("Success! File ID:", resp["file_id"])
    print("Download link:", url + "/files/download/" + resp["file_id"])


if __name__ == '__main__':
    main()
