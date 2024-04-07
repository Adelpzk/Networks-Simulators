# Lab2

## Task 1 Instructions

In this task, you will be starting a web server. To get started, you 
need to download the webserver source file, and the HTML files on your
machine.

### Installation

First, you need to download the necessary files:
- `webserver.py`
- `HelloWorld.html`
- `404.html`

Ensure the 404.html and HelloWorld.html file is in the same directory as the webserver.py file to proceed with running the program.

### Running the Server

Open your command line interface and navigate to the directory containing the downloaded files. Run the following command to start the web server:

```bash
python3 webserver.py
```

You should now be able to access the web server from your browser at http://127.0.0.1:10200/. This will automatically show you to the contents of the 404 HTML file as there is no file to be returned at http://127.0.0.1:10200/. To view the HelloWorld.html, enter http://127.0.0.1:10200/HelloWorld.html in the browser.

You can add other HTML files into the same directory as the webserver.py source file. The web server will still work if you have files nested in directories as long as the root directories are in the same location as webserver.py. To access these files, simply enter http://127.0.0.1:10200/directory_name/file_name


## Task 2 Instructions

In this task, you will be working with a client-server architecture. To get started, you need to download both the client and the server on your machine.

### Installation

First, you need to download the necessary files:

- `client.py`
- `server.py`

Ensure both files are in the same directory to proceed with running the programs.

### Running the Server

Open your command line interface and navigate to the directory containing the downloaded files. Run the following command to start the server:

```bash
python3 server.py
```

### Running the client

After you have the server running, you can start the client in a new command line interface window. Navigate to the directory where client.py is located and run:

```bash
python3 client.py
```
