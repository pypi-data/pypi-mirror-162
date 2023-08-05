
## Cage - remote file access system
### &nbsp;
### Remote file access on computers on the network. The system supports all major file operations (create, open, delete, read, write etc.) by exchanging transactions via TCP.
### &nbsp;
### Tags: _remote, file system, file server, file sharing, file system api_
### &nbsp;
###  Field of application
The functionality of the system is effective in the following cases:
  * in native applications for mobile and embedded devices (smartphones, on-board control systems, etc.) requiring quick access to files on remote servers in conditions of probable temporary interruptions in the connection (with going offline);
  * as a physical layer for creating a DBMS in which query processing is performed on some servers, and data is stored on others;in loaded DBMS, if request processing is performed on some servers, but data storage on others;
  * in distributed corporate networks requiring high speed data exchange, redundancy and reliability;
  * in complex systems with microservice architecture, where delays in the exchange of information between modules are critical.
###  Structure
Cage system includes two main parts:
1. `Cageserver` \- a server-side program (Python functions with the main program), which runs on computers on the network whose files require remote access;
2. PyPI package `cage-api`, which includes modules:
    * `cage.py` - contains main class of the system `Cage`, whose methods provide remote file operations in applications;
    * `cage_channel.py` - contains support functions for Cage class methods;
    * `cage_page.py` - contains low-lewel function for page buffering of remote files; 
    * `cage_err.py` - contains classes and function for errors and exceptions processing;
    * `thread_write_page.py` - contains function `page_write`, which used only if the mode of parallel transfer of modified pages of deleted files to the file server in thread is allowed;
    * `cage_par_cl.py` - settings file. 

#### Repository `Arselon/Cage` includes only Part 2: `cage-api`, that is used on the client side (in applications). 
### &nbsp;
![Block diagram](https://business-on.herokuapp.com/static/images/article_images/cage_1.jpg)
###  Using the system on the client side
The methods of the Cage class replace the usual, "routine" operations of the
local file system: _creating, opening, closing, deleting_ files, as well as
_reading/writing data in binary format_. Conceptually, these methods are close
to the file functions of the C language, where file actions is done "through
the channels" of input/output.

In other words, the programmer does not work with methods of built-in file
functions or classes (for example, class `_io` in Python), but with methods
of class Cage.

When the Cage object is created (initialized), it establishes the initial
connection with the server (or several servers), is authorized by the client
identificator, and receives a confirmation with a dedicated port number for
all file operations. When Cage object is deleted, it issues a command to the
server to terminate the connection and close the files. Termination of
communication can also be initiated by the servers themselves.

A single Cage object can communicate with multiple files on multiple servers.
Communication parameters (server IP address or DNS, primary port for
authorization, path and file name) are set when creating the object.
Because each Cage object can handle multiple files at the same time, a common
memory space is used for buffering. The system improves read/write performance
by buffering frequently used by the client application file fragments in the
RAM cache (memory buffer).

Cache size - the number of pages and their size is set dynamically when
creating a Cage object. For example, 1 GB cache means 1,000 pages of 1 MB
each, or 10,000 pages of 100 KB, or 1 million pages of 1 KB. The choice of
page size and number is a specific optimization task for each application.
Client software can use any number of Cage objects with different settings
(memory buffer size, block (chunk) size, etc.). Can be used multiple Cage
objects at the same time to define different buffer memory settings depending
on how you access information in different files.

As a basic, the simplest buffering algorithm is used: after exhausting a given
amount of memory, new pages displace old ones on the principle of recycling
with a minimum number of hits. Buffering is especially effective in the case
of uneven (in a statistical sense) sharing, first, to different files, and,
secondly, to fragments of each file. To speed up the application for reading
data, you can enable a special mode for pushing pages to the file server in a
separate thread.

Cage class supports input/output not only by data addresses (specifying the
position and length of the array in a file), but also at a lower level - by
page numbers.
For Cage objects, the original _hibernation_ (sleep) function is supported.
They can be "minimized" (collapsed) to a local dump file on the client side
and quickly restored from this file (after resuming communication, when the
application restarts). For example, in case of disconnection with servers, or
when the application is stopped, etc. This makes it possible to significantly
reduce traffic when activating the client program after a temporary "offline",
as often used fragments of files will already be in application memory.
### &nbsp;
###  **Server operation**
`Cageserver` program can be run with an arbitrary number of ports, one of
which ("primary" or "main") is used only for authorization of all clients, and
the others - for data exchange.
The server starts as two main processes:
  1. "Connections" \- the process for establishing communication with clients and for its termination;
  2. "Operations" \- the process for execution of tasks (operations) of clients on working with files, and also for closing of communication sessions on commands of clients.
Both processes are are not synchronized and organized as endless cycles of
receiving and sending messages based on multi-process queues, proxy objects,
locks, and sockets.

The Connections process provides each client with one "secondary" port for
data transfer. The total number of secondary ports is set at server startup.
The correspondence between secondary ports and clients is stored in proxy
memory between processes.

The Operations process supports the separation of file resources, and several
different clients can read data from one file together ( _quasi-parallel_ ,
since access is controlled by locks) if it was allowed when the "first" client
initially opened the file.

Processing of commands (tasks) to create/delete/open/close files on a server
is performed in Operations process strictly sequentially using the file
subsystem of the server OS.

For general read/write acceleration, these tasks are performed in threads
created by the Operations process. The number of threads is usually equal to
the number of open files. But read/write tasks from clients are submitted to
the common shared queue and the first thread that is freed takes the task out
of the queue head. Special logic excludes data rewriting operations in server
memory.

The Operations process monitors the activity of clients and stops their
service both by their commands and when the inactivity timeout is exceeded.
To ensure reliability, Cageserver may keeps logs of all transactions. One
common log may contains copies of all messages from clients with tasks to
create/open/rename/delete files. For each working file, a separate log may
contains copies of messages with tasks for reading and writing data. Arrays of
written (new) data and arrays of data that were destroyed when overwriting can
be saved. These logs can provide the ability to both restore new changes to
backups and to "roll back" from the current content to the desired point in
the past.  

_Note: In the published version, there is no functionality for logging and
rollbacks, since it is in the debugging stage. It is also planned to improve
authentication mechanisms and control access levels to files._
### &nbsp;
###  Transaction formats
Messaging between servers and client applications is based on the
"Request–Reply" protocol of  [ZeroMq system](https://github.com/zeromq/pyzmq ). Servers as receivers wait
messages from senders - clients via TCP.
There are two transaction channels:
1. To establish a connection.  
2. To perform file operations. 
### Communication procedure
  1. Client requests a TCP connection from the socket on the server's main (primary) port (common to all clients).
  2. If the connection is established, the client requests the port number, allocated to it by the server for performing file operations:  
      * Request from client: `( { ident.client }, "connect", { ident.request })`, where:  `ident.client` - a unique token for authorizing client access to file server resources,  `ident.request` - the sequence number of the client's request to this server (used for additional protection against attempts to interfere).
      * The server responds: `({ ident. client }, { N port }, { ident. request }, { status } )`. 
      * If `{ status } = "connected"`, the the second element of the tuple contains the number of the secondary port for transaction exchange.
  3. The client requests a second TCP connection socket from the server on the secondary port.
  4. If the connection is established, the Cage object is ready to go.
### &nbsp;
### The procedure for the exchange of transactions
#### &nbsp;
#### **For all operations except write/read**:  

Request from the client: `({ operation }, { ident. client }, { op.1 }, {
op.2 }, { op.3 }, { ident. request })`  

  `{ operation }` is the operation code ("n", "o", "c", etc. - see below), 

  `{ op.1 }`, `{ op.2 }` and `{ op.3 }` is the operands that are specific to each operation  

  Operations:
  * "n" - create a new file, 
    * `{ op.3 }` - path and file name  
  * "o" - open the file, 
    * `{ op.3 }` - path and file name,
    * `{ op.2 }` - opening status: "wm" - full monopoly (read/write), "rs" - read-only, and shared read-only for other clients, "ws" - read/write, and shared read-only for other clients.  
  * "c" - close file 
    * `{ op.2 }` - number of the file's "channel" (see below the description of the Cage class)  
  * "u" - rename the file, 
    * `{ op.2 }` - the new file name, 
    * `{ op.3 }` - the path and the old file name  
  * "d" - delete file, 
    * `{ op.3 }` - path and file name  
  * "x" - get information (statistics) about all channels  
  * "i" - get information about the channel, 
    * `{ op.2 }` - file channel number  
  * "t" - end of communication with the server  
  * "e" - execute of the script on the server, 
    * `{ op.3 }` - text of a Python script.  

After attempting to perform the requested operation, the server responds to
the client with a message in the same format, and if the result is successful,
the first element contains the operation code, if not successful - the
operation code + the character "e", for example, "ne", "oe", and the like. In
case of an error, the fourth element of the server response (instead of {
op.3 }) contains a detailed diagnostics of the error (or sequence of errors)
from the server.
#### &nbsp;
#### **Reading** data from a file and **writing** to a file are performed not in 2 steps, like other operations (request-response), but in 4 steps.:  
  * For writing: 
    1. request from the client to write `("w", { ident. client }, { channel number }, { (offset, length) },"", { ident. request })`
    2. server response about readiness to recieve data: `(b"\x0F"\*4)` - can continue,  `(b"\x00"\*4)` - error 
    3. sending data to the server: `({ binary array })`, in which data and metadata are serialized
    4. confirmation from the data acquisition server and the result - is successful or failed.
  * For reading: 
    1. request from the client to read `("r", { ident. client }, { channel number }, { (offset, length) },"", { ident. request} )`
    2. server response about readiness to send data: `(b"\x0F"\*4)` - can continue, `(b"\x00"\*4)` - error
    3. confirmation from the client that it is ready to accept data
    4. sending data to the client: `({ binary array })`, in which data and metadata are serialized, or contain information about the error.
### &nbsp;
###  **Emulation of the remote server on a local computer**
#### &nbsp;
Starting from the 3rd version (August 2022), the **Cage system** software supports emulation 
of a remote server on a local (client) computer - i.e. on the one on which 
the application with the `Cage` class is executed.

To "enable" this mode, it is enough to specify the full path to the folder 
containing the files as the value of the `local_root` parameter (see below)
when creating an instance of the `Cage` class. In this case, instead of 
establishing connections with the **Cageserver** file server and 
performing all file operations remotely, the software will bypass 
them and work directly with the OS file system of the client computer.

The use of a non-empty valid `local_root` parameter value is a "trigger" 
that replaces all transactional logic with routine operations 
of the local OS file system. No other changes to the program code are required. 
All methods and functions will not require additional parameters. 
Thus, the API remains unchanged, except using 
parameter `local_root` for the emulation (when creating instances of `Cage` class).

Remote server emulation is useful when developing, debugging, and testing 
client software that uses the **Cage system**.
### &nbsp;
###  **Cage API**
#### &nbsp;
#### **Settings**

Default values of system parameters specified in `cage_par_cl.py` module and they can be redefined in applications, taking into account the available RAM for the cache of remote files, optimum size of the pages, and other features.
- `PAGESIZE` = 64 * 2 ** 10  - (64Kb) - size of one page in buffer in **bytes**;
- `NUMPAGES` = 2 ** 10  - (1024) - number of pages in buffer;
- `MAXSTRLEN` = 64 * 2 ** 20  - (64Mb) - max length (amount) of byte's of trnferring data arrays in read/write file operations in **bytes**;
- `CAGE_SERVER_NAME` = "cage_server" - a conditional name for the main application server. It should be borne in mind that the class Cage allows to simultaneously work with several servers, which, respectively, should have different names defined;
- `DEFAULT_SERVER_PORT` = "127.0.0.1:3570" - default file server ip and "main" port;
- `ATTEMPTS_MAKE_CONNECTION` = 5 - max. number of attempts to connect with each file server This affects the operation of the message transfer package ZeroMQ that is used in the Cage system for data exchange between file servers and applications;
- `CONNECTION_TIMEOUT` = 5 - **seconds** - timeout between attempts to connect with file server;
- `ATTEMPTS_GET_RESPONSE` = 5 - max. number of attempts to get response from server;
- `GET_RESPONSE_TIMEOUT` = 5 - **seconds** - timeout for recieving common & client ports from server;
- `RESPONSE_TIMEOUT` = 5000 - **milliseconds** - timeout get response from server;
- `WRITE_THREAD` = **False**  #   True or no threading while write pushed page;
- `CACHE_FILE` = "cage" - default prename for first cache file during first cage instance (in application) sleeps;
- `CACHE_FILE2` = "cage2" - default prename for second cache file during second cage (in application) sleeps;
- `SPLITTER` = b"\x00"*4 - a string to separate (split) `cage_id` and JWToken in `cage_name`;
- `CAGE_SERVER_WWW` = '' - it is used in applications to set the DNS and the main port, for example: "ec2-11-222-333-444.eu-west-3.compute.amazonaws.com:3570";
- `CAGE_DEBUG` =  **True** - in prodiction must be **False**
#### &nbsp;
## Class `Cage` 
### `(cage_name= "...", pagesize=, numpages=, maxstrlen=, server_ip=, local_root=, wait=, awake=, cache_file=, zmq_context=, mode=)`
From this class objects are created that interact with file servers. Each
object (instance) of the Cage class for any Cageserver - is one independent
"client" in the network.
### Required parameters
- `cage_name` ( _str_ ) - `the conditional name of the object used to identify clients on the server side` + `(b"\x00" * 4).decode('utf-8')` + `JSON Web Token` (see https://pyjwt.readthedocs.io/en/latest/). `cage_name` used in in file servers to identify client applications. JSON Web Token in the Cage system carries an authentication function for security during data exchange and also contains information about access rights. For more details, see the technical documentation for the Cage system; 
- one of two alternatives:
  * `server_ip` ( _dict_ ) - a dictionary with the addresses of the servers used, where the _key_ is the _conditional name_ of the server (server name used in program code of the application), and the _value_ is a string with _real server address: `ip address:port`_ or _` DNS:port `_. Matching names and real addresses is temporary, it can be changed (by default `{"default_server_and_main_port": DEFAULT_SERVER_PORT}`); 
  * `local_root` ( _str_ ) - full path (URL) to the folder with the database files on the local computer. A non-empty valid value for this parameter enables the fileserver **emulation mode** (see above) and invalidates the parameters `server_ip`, `zmq_context` and `wait`; 
- `mode` ( _str_ ) - HT files access mode: 
  * "rm" - readonly with monopoly; 
  * "rs" - readonly in sharing mode;  
  * "wm" - (by default) read and write with monopoly; 
  * "ws" - write with monopoly and read in sharing mode;  
  * "sp" - special mode for administrator; 
### Additional parameters
- `pagesize` ( _int_ ) - size of one page of buffer memory (in bytes, by default PAGESIZE); 
- `numpages` ( _int_ ) - number of pages of buffer memory (by default NUMPAGES); 
- `maxstrlen` ( _int_ ) - maximum length of the byte string in write and read operations (in bytes, by default MAXSTRLEN); 
- `wait` ( _int_ ) - time to wait for a responses from the server (in seconds, by default GET_RESPONSE_TIMEOUT); 
- `awake` ( _bool_ ) - the flag of the method of creating the object: _False_ \- if a new object is created, _True_ \- if the object is recovered from previously hibernated in cache file (by default _False_ ); 
- `cache_file` ( _str_ ) - local file prename for hibernation (by default CACHE_FILE);
- `zmq_context` ( _object_ ) - Python bindings for ZeroMQ (see https://pyzmq.readthedocs.io/en/latest/api/zmq.html), by default `False`, which means the ZeroMQ context will be created in the Cage object itself; 
#### &nbsp;
### Cage methods
#### &nbsp;
### `file_create` 
#### `(server, path, Kerr=[])` 
Create a new file
#### R e c e i v e s
  * `server` \- the conditional server name; 
  * `path` \- full path to the file on the server; 
  * `Kerr` \- list with information about error, which created/updated by error processing functions in **cage_err** module included in the package **cage-api**.
#### R e t u r n s
  * `True` \- on success; 
  * `False` \- for a system error (I/O, communication, etc.). In this case **Kerr** parameter will contain detailed information ; 
  * `ReturnCode` \- if the file was not created, but this is **not** an error (a numeric return code can only be obtained if the emulation mode is not used):   
    **-1** - if a file with the same name already exists and is closed;   
    **-2** - if a file with the same name already exists and is opened by this client;   
    **"wm", "rs"** or **"ws"** - if a file with the same name already exists and is opened
by another client in the corresponding mode (see the Cage.open method below).
#### &nbsp;
### `file_rename`
#### `(server, path, new_name, Kerr=[])` 
Rename the file
#### R e c e i v e s
  * `new_name` \- new file name. 
#### R e t u r n s
  * `True` \- if the file was successfully renamed; 
  * `False` \- if the file does not exist, or temporaly blocked, or due to a system error; 
  * `ReturnCode` \- if the file was not created, but this is **not** an error (a numeric return code can only be obtained if the emulation mode is not used):   
    **-2** - if a file with the new name already exists;   
    **-3** - in use by other clients in shared modes; 
#### &nbsp;       
### `file_remove` 
#### `(server, path, Kerr=[])` 
Delete file
#### R e t u r n s
  * `True` \- if the file was deleted successfully; 
  * `False` \- if the file does not exist, or temporaly blocked, or due to a system error. 
#### &nbsp;
### `open` 
#### `(server, path, mod=)` 
Open file
#### R e c e i v e s
- `mod` \- file open mode:   
  * "rm" - readonly with monopoly; 
  * "rs" - readonly in sharing mode;  
  * "wm" - (by default) read and write with monopoly; 
  * "ws" - write with monopoly and read in sharing mode;  
  * "sp" - special mode for administrator; 
#### R e t u r n s
  * `ReturnCode` = `fchannel` \- if the file was successively open, `fchannel` - is a positive integer - "channel number" assigned or already existing (that is, the file was previously opened by this client); 
  * `False` \- if the file does not exist, or already opened by this client in another mode, or temporaly blocked, or when the limit on the number of open files is exceeded, or when the system error. 
#### &nbsp; 
### `close` 
#### `(fchannel, Kerr=[])` 
Close the file
#### R e c e i v e s
  * `fchannel` \- channel number. 
#### R e t u r n s
  * `True` \- if the file was successfully closed for the client (physically or "virtually"). If the first client closes the file that other clients use in addition to it, the server does not physically close the file, and the first in order remaining client becomes the "owner";
  * `False` \- if the file is not closed due to an error in the channel number or due to a system error.
#### &nbsp;      
### `write` 
#### `(fchannel, begin, data, Kerr=[])` 
Write the byte string to the file
#### R e c e i v e s
  * `begin` \- the first position in the file (from zero or more); 
  * `data` \- string of bytes. 
#### R e t u r n s
  * `True` - if the recording was successful; 
  * `False` in case of an error in the parameter values, or inability to record due to the file channel mode, or temporaly blocked, or in case of a system error. 
  #### &nbsp;   
### `read`
#### `(fchannel, begin, len_data, Kerr=[])` 
Read the byte string from the file
#### R e c e i v e s
  * `len_data` \- string length (bytes). 
#### R e t u r n s
  * `byte string` \- if reading was successful; 
  * `False` \- if there is an error in the parameter values, or with a system error. 
#### &nbsp;  
### `is_active` 
#### `(fchannel, Kerr=[], get_f_status= False)` 
Test number as cage channel and returm mode for cage operations and OS status on file server
#### R e c e i v e s
  * `get_f_status`(_bool_) \- Need or no to get channel mode. Applicable only if the emulation mode is not used. 
#### R e t u r n s
- if the emulation mode is not used
  * `Object` with information \- if successful. 
    - `Object` is the tuple: `(internal channel number of file server, channel mode)` if `get_f_status` == `True`, or 
    - `(internal channel number of file server)` if `get_f_status` == `False`; 
  * `False` \- in case of an error in the fchannel value, or in case of a system error. 
- if the emulation mode is used  
  * `True` \- if the channel is exist and opened; 
  * `False` \- if the channel is not exist or was closed.
#### &nbsp; 
### `remote`
#### `(server, Kerr=[])` 
Get general information about all channels opened on the server.
#### R e c e i v e s
  * `server` - server name. Applicable only if the emulation mode is not used. 
#### R e t u r n s
- if the emulation mode is not used
  * `object` with information \- if successful. `Object` is the list of the lists `[[(common_tuple)],[(channel_tuple),...]]`, where `common_tuple`=`(server name, communication port, common number of page loads, common number of page uploads)`, `channel_tuple`=`(channel number, number of page loads, number of page uploads, file name, file mode)`; 
  * `False` in case of an error in the parameter value, or in case of a system error. 
- if the emulation mode is used  
  * `String`  with information with modes for all opened channels.  
#### &nbsp; 
### `put_pages`
#### `(fchannel, Kerr=[])` 
Pushes from the buffer to the server all pages of the specified channel that have been modified. It is used at those points in the algorithm when you need to be sure that all operations on the channel are physically saved in a file on the server.
#### R e t u r n s
  * `True` \- if the recording was successful; 
  * `False` \- if there is an error in the parameter value, or an inability to write due to the channel mode of the file, or with a system error. 
#### &nbsp; 
### `push_all`
#### `(Kerr=[])` 
Push from the buffer to the server all pages of all channels for the `Cage` class instance that have been modified. Used at those points in the algorithm when you need to be sure that all operations on all channels are saved on the server.
#### R e t u r n s
  * `True` \- if the recording was successful; 
  * `False` \- if there is a system error. 
#### &nbsp;   
### `refresh` 
#### `(Kerr=[])` 
Rrefresh all pages of those opened files who was modified outwardly
#### R e t u r n s
  * `True` \- if the recording was successful; 
  * `False` \- if there is a system error. 
#### &nbsp;   
### `sleep` 
#### `(Kerr=[])` 
Hibernation - record cage memory into cache file and delete cage instance. Applicable if the emulation mode is not used. 

Recovering cage memory from file, socket connecting with server and open channels after sleeping and bebuilding dict `cage_ch` - are executed when an instance of the Cage class with a parameter `awake=True` is created.
#### R e t u r n s
- if the emulation mode is not used
  * `True` \- if the recording was successful; 
  * `False` \- if there is a system error.
- if the emulation mode is used - always `False`.  
### &nbsp;
## Class **`DictDiffer`** 
### `(current_dict, past_dict)`
Calculate the difference between two dictionaries. See [fcmax.livejournal.com](https://fcmax.livejournal.com/10291.html)
### Required parameters
- `current_dict` (_dict_) - sample dictionary;
- `past_dict` (_dict_) - tested dictionary.
#### &nbsp;
### Methods
##### &nbsp;
### **`added`** 
#### `()` 
#### R e t u r n s
- (_set_) - The set of new items (added).
##### &nbsp;
### **`removed`** 
#### `()` 
#### R e t u r n s
- (_set_) - The set of deleted items (removed)
##### &nbsp;
### **`changed`** 
#### `()` 
#### R e t u r n s
- (_set_) - The set of the _keys_ same in both dicts but changed _values_.
##### &nbsp;
### **`unchanged`**
#### `()`  
#### R e t u r n s
- (_set_) - The set of the _keys_ same in both dicts and unchanged _values_.
### &nbsp;
## Class **`CageERR(Exception)`** 
### `()`
Class for error processing in `Cage` package.
### &nbsp;
## Class **`Logger`** 
### `(term=False)`
Class for redirecting system outstream (print function).

`Log_print` = "cage_print.txt"  - default filename for copying/redirecting system outstream(printing).
### Required parameter
- `term` (_bool_):
  * `True` - system outstream writes to log file `Log_print` and copy outstream redirects to terminal window;
  * `False` - (by default) system outstream writes only to log file `Log_print`. 
### &nbsp;
### **"External" functions for debugging, errors and exceptions processing**
#### &nbsp;
`Log_err` = "cage_error.log"  # default errlog filename.

'Kerr` - list of the errors description in the sequence of their appearance. Each item - list with the error description.
#### &nbsp;
### **`pr`** 
#### `(message="", func="", proc_inf=False, cage_debug= CAGE_DEBUG, wait=0.0, tim=True)`
Debug messages generating: record prints to `Log_err` file and printing to stdot if `cage_debug=True`. 
#### R e c e i v e s 
* `message` \- text for message; 
* `func` \-  name of module, function or class method from what message originated;
* `cage_debug`: 
  * `True` - function `pr` in progress;
  * `False` - function `pr` not executed.
* `tim`:
  * `True` - in message additional time information included - `datetime.datetime.now()`
  * `False` - additional time information not included.
* `proc_inf`:
  * `True` - in message additional information about threading and subprocessing included:
    * `os.getppid()` - parent process;
    * `os.getpid()`  - self process;
    * `threading.get_ident()` - thread.
  * `False` - additional information about threading not included.
* `wait` (_int_) - executed `time.sleep(wait)` (milliseconds) before each write to `Log_err` file - for comfort in parallel environment.
#### &nbsp;
### **`set_warn_int`** 
#### `(Kerr, inst, func="", int_err="", message="", cage_debug=False,)`
Set **warning** code "w" to error list "Kerr", write record to `Log_err` (if `CAGE_DEBUG=True`) and generate debugging message.
#### R e c e i v e s 
  * `Kerr` \- list with information about error in internal Cage format;
  * `inst` - name of module or class instance from what message originated;
  * `func` - name of function or class method from what message originated;
  * `int_err` - serial internal Cage system error number in function or method;
  * `message`- text for message;
  * `cage_debug`:
    * `True` - generate debugging message calling function `pr`;
    * `False` - not generate debugging message.

Error item structure: `("w", instance.__class__.__module__, instance.__class__.__name__, func, str(int_err), datetime.datetime.now())`
#### &nbsp;
### **`set_err_int`** 
#### `(Kerr, inst, func="", int_err="", message="", cage_debug=True,)`
Set **serious program error** code "e" to error list "Kerr", write record to `Log_err` (if `CAGE_DEBUG=True`) and generate debugging message.
    
Error item structure: `("e", instance.__class__.__module__, instance.__class__.__name__, func, str(int_err), datetime.datetime.now())`
#### &nbsp;
### **`set_err_syst`** 
#### `(Kerr, inst, func="", int_err="",  OSsubsyst="", pathfile="",  sys_err="", message="", cage_debug=True,)`
Set **system error** code "s" to error list "Kerr", write record to `Log_err` (if `CAGE_DEBUG=True`) and generate debugging message.

This function used usually for record info about OS exceptions.
#### R e c e i v e s 
  * `OSsubsyst` - OS subsytem conditional name;
  * `pathfile` - path for OS file system errors;
  * `sys_err=` - OS error code generated by exception.
    
Error item structure: `("s", instance.__class__.__module__, instance.__class__.__name__, func, str(int_err), datetime.datetime.now(), OSsubsyst, pathfile, sys_err,)`  
#### &nbsp;
### **`is_err`** 
#### `(Kerr, types="*")`
Check `Kerr` list for presense serious "e" and/or system "s" errors.
#### R e c e i v e s 
  * `Kerr`- list with information about errors in internal Cage format;
  * `types`:
    * "e" - check for serious "e" errors;  
    * "s" - check for system "s" errors; 
    * "*" - check for serious "e" or for system "s" errors;
#### R e t u r n s
  * `-1` - errors not found;
  * `index` - the ordinal number (index) of the first found sublist with an error in `Kerr` list.
#### &nbsp;
### **`zero_Kerr`** 
#### `(Kerr, type=("s","e"), my_debug=False)`
Set `Kerr` list  empty.
#### R e c e i v e s 
  * `Kerr`- list with information about errors in internal Cage format;
  * `type` - the tuple with errors type need to delete;
  * my_debug:
    * `True` - function `zero_Kerr` in progress;
    * `False` - function `zero_Kerr` not executed.

### &nbsp;
____________________
#### _Copyright 2019-2022 [Arslan S. Aliev](http://www.arslan-aliev.com)_

_Software licensed under the Apache License, Version 2.0 (the "License"); you may not use this software except in compliance with the License. You may obtain a copy of the License at [www.apache.org](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License._  

###### Cageserver v.4.1, Cage package v.3.1.0, readme.md red.04.08.2022


