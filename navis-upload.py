#!/usr/bin/env python

import argparse
import os
import sys
import threading

import boto3

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def upload(bkt, src, dst):
    s3 = boto3.client('s3')

    with open(src, 'rb') as f:
        s3.upload_fileobj(f, bkt, dst, Callback=ProgressPercentage(src))
        print()


def main():
    parser = argparse.ArgumentParser(description='Upload a file to an S3 bucket.')
    parser.add_argument('--bucket', required=True, help='the bucket name')
    parser.add_argument('source', nargs=1, help='the file path to be watched')
    parser.add_argument('destination', nargs=1, help='the destination file')

    args = parser.parse_args()

    bucket = args.bucket
    source = args.source[0]
    destination = args.destination[0]

    upload(bucket, source, destination)

if __name__ == '__main__':
    main()
