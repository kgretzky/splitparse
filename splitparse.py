#!/usr/bin/python

import argparse
import glob
import os, os.path
import sys
import zlib
from http_parser.parser import HttpParser

def parse_http_packet(headers, body):
    ret = ''
    for key, value in headers.items():
        ret += key + ': ' + value + '\n'
    ret += '\n'
    
    dec_body = ''
    if 'Content-Encoding' in headers:
        if headers['Content-Encoding'] == 'gzip':
            try:
                dec_body = zlib.decompress(body, 16+zlib.MAX_WBITS)
            except:
                pass
            
    if dec_body == '':
        dec_body = body

    ret += dec_body
    ret += '\n'
    return ret

def convert_str(s):
    ret = ''
    table = 'abcdefghijklmnopqrstuvwxyz0123456789.-'

    for c in s:
        if c in table:
            ret += c
        else:
            ret += '_'
    return ret

def save_http_packet(outdir, orig_filename, hostname, path, rtype, data):
    fn = orig_filename + '_' + rtype + ' ' + convert_str(path)[:32] + '.txt'
    save_dir = os.path.join(outdir, convert_str(hostname[:32]))

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with open(os.path.join(save_dir, fn),'wb') as f:
        f.write(data)

def process(indir, outdir):
    findstr = os.path.join(indir, '*')
    for fn in glob.glob(findstr):
        print fn
        with open(fn, 'rb') as f:
            http_bin = f.read()

        n = 0
        while n < len(http_bin):

            http = HttpParser()
            nparsed = http.execute(http_bin[n:], len(http_bin) - n)

            if not http.is_message_complete():
                break

            if http.get_path() != '':
                # send

                http_method = http_bin[n:].split()[0] #http.get_method() -- seems bugged
                http_path = http_bin[n:].split()[1]
                http_request = parse_http_packet(http.get_headers(), http.recv_body())
                http_hostname = 'unknown'
                if 'Host' in http.get_headers():
                    http_hostname = http.get_headers()['Host']
                print http_hostname

                nparsed -= 1

                full_http = http_method + ' ' + http_path + '\n'
                full_http += http_request + '\n'

                save_http_packet(outdir, os.path.basename(fn), http_hostname, http_path, 'send', full_http)
            else:
                # recv

                http_status = http.get_status_code()
                http_reply = parse_http_packet(http.get_headers(), http.recv_body())
                
                full_http += str(http_status) + '\n'
                full_http += http_reply

                save_http_packet(outdir, os.path.basename(fn), http_hostname, '', 'recv', full_http)

            n += nparsed

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dir", help="Input directory with sslsplit log files.", required=True)
    parser.add_argument("-o", "--output-dir", help="Output directory.", required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    process(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()