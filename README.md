
# ParallelFileDownloader

# Description
This program downloads an index file to obtain a list of text file URLs and download these files in parallel. Multitheading is used in order to be able to download parts of a file in parallel. For this program no third party HTTP client libraries, or the HTTP specific core or non-core APIs are used. The program is implemented using Socket package default in Python.


# Command
    python3 ParallelFileDownloader.py <index_file> <connection_count>

command, where \<index_file> is the URL of the index that includes a list of text file URLs to be downloaded and \<connectioncount> is the number of connections to be established for each file URL.


# Details
When a user enters the command above, the program sends an HTTP GET request to the server in order to download the index file with URL \<index_file>. If the index file is not found, the response is a message other than 200 OK. In this case, the program prints an error message to the command-line and exits. If the index file is found, the response is a 200 OK message. When this is the case, the program prints the number of file URLs in the index file and send an HTTP HEAD request for each file URL in the index file.

Requested file is not found If the requested file is not found in the server, the response is a message other than 200 OK. In this case, the program prints a message to the command-line indicating that the file is not found.

Requested file is found If the requested file is found in the server, the response is a 200 OK message. When this is the case, the program establishes \<connection_count> parallel connections with the server including the file, downloads non-overlapping parts of the file through these connections, constructs and saves the file under the directory in which the program runs. The name of the saved file is the same as the downloaded file and a message indicating that the file is successfully downloaded is printed to the command-line.

# Examples
Let www.foo.com/abc/index.txt be the URL of the file to be downloaded whose content is given as

    www.cs.bilkent.edu.tr/file.txt 
    www.cs.bilkent.edu.tr/folder2/temp.txt wordpress.org/plugins/about/readme.txt 
    humanstxt.org/humans.txt

where the first file does not exist in the server and the sizes of the other files are 6000, 4567, and 1589 bytes, respectively.

**Example run 1** Let the program start with the

    python3 ParallelFileDownloader.py www.foo.com/abc/index.txt 3

command. Then all files except the first one in the index file are downloaded. After the connection is terminated, the command-line of the client may be as follows:

    Command-line:
    URL of the index file: www.foo.com/abc/index.txt Number of parallel connections: 3  
    Index file is downloaded  
    There are 4 files in the index
    1. www.cs.bilkent.edu.tr/file.txt is not found  
    2. www.cs.bilkent.edu.tr/folder2/temp.txt (size = 6000) is downloaded File parts: 0:1999(2000), 2000:3999(2000), 4000:5999(2000)  
    3. wordpress.org/plugins/about/readme.txt (size = 4567) is downloaded File parts: 0:1522(1523), 1523:3044(1522), 3045:4566(1522)  
    4. humanstxt.org/humans.txt (size = 1589) is downloaded  
    File parts: 0:529(530), 530:1059(530), 1060:1588(529)

**Example run 2** Let the program start with the

    python3 ParallelFileDownloader.py www.foo.com/abc/index.txt 5

command. Then all files except the first one in the index file are downloaded. After the connection is terminated, the command-line of the client may be as follows:

    Command-line:
    URL of the index file: www.foo.com/abc/index.txt Number of parallel connections: 5  
    Index file is downloaded  
    There are 4 files in the index
    1. www.cs.bilkent.edu.tr/file.txt is not found  
    2. www.cs.bilkent.edu.tr/folder2/temp.txt (size = 6000) is downloaded  
    File parts: 0:1199(1200), 1200:2399(1200), 2400:3599(1200), 3600:4799(1200), 4800:5999(1200)  
    3. wordpress.org/plugins/about/readme.txt (size = 4567) is downloaded  
    File parts: 0:913(914), 914:1827(914), 1828:2740(913), 2741:3653(913), 3654:4566(913)  
    4. humanstxt.org/humans.txt (size = 1589) is downloaded  
    File parts: 0:318(318), 318:635(318), 636:953(318), 954:1271(318), 1272:1588(317) 



