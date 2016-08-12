## SplitParse

Short script using buggy **http-parser** library to decode output logs of *sslsplit* raw HTTP packets.
Decoded packets are organized into proper directory structure and saved in clear-text form.

* Decodes *Transfer-Encoding: chunked*
* Decompresses *gzip* compression of packets
* Puts output packets in directories with the name of corresponding domain, the request was made to.

###### Installation

```
pip install http-parser
./splitparse.py -i [input_dir] -o [output_dir]
```

###### Epilogue

Note: Really buggy, but "good enough". I couldn't get around the **http-parser** bugs and I believe it would be easier to write your own HTTP parser for professional use.

