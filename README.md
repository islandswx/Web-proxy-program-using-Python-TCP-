# Web-proxy-program-using-Python-TCP
A web-proxy program to act as a proxy between client (browser) and web-server - supports caching and prefetching.

Author: Pratik Lotia

Function: A python script which acts as a proxy server between client and actual server*

*Valid only for 'GET' requests and HTTP version 1.0 and 1.1 only

Python programs executable in v3.1 and higher versions (done on v3.4)

Usage (on command line / command prompt): webproxy <proxy_port> <cache_timeout_value>

Note: Proxy port should be > 1024 and < 65535; it should be set in browser settings
Cache timeout (in seconds) should be positive float value; ideal value depends on type of server; for dynamic servers set it
to '0'.


Set proxy settings in your browser: with port number same as the one entered above and proxy as 'localhost'
Note:
1. Caching supported
2. Prefetching supported
3. Error handling supported
4. Keyboard Interrupt supported

Functional process:
Proxy accepts requests from client and generates a thread which finds the webserver and port to which it should
connect.
It first checks if the (hash of the) path (filename) is present in its cache. If present, it sends the file from
its cache storage.
Else, A socket is created to connect to webserver and port. Default port is set to 80.
(Currently, HTTPS - port 443) is not supported.
Proxy requests the path (filename or directory) to the webserver and receives it. Hash value of path is stored
in cache and timer is started - dictionary: key-value pair is used for this purpose.
The cache files are created and stored in the proxy script directory.

Another thread is created which prefetches the future links which the client might request for and stores them
in the cache (and files are created as above). The prefetching is implemented by requesting files found from
'a href' lines in the html files.
If the client requests the page later (within the timeout value), the file is sent from cache.

Errors shall be received for invalid method, http type, etc.

Note:
While implementing cache, this program shall actually write the cache files in your program directory. However, the files have been 'written' including the header part so they will not open properly. You can edit the program to 'write' only the data part.
Also, if you do not want cache files to get 'written' in your directory, you could implement it using dictionary key-value pair.

I find that on Windows you can change the console encoder to utf-8 or other encoder that can represent your data. Then you can print it to sys.stdout.
First, run following code in the console (command prompt):

chcp 65001 (Then press ENTER)

set PYTHONIOENCODING=utf-8 (Then press ENTER)


Then, start the webproxy as instructed above.

