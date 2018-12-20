# DuckCard: newly admitted students' ID card printing data process tool

The DuckCard is made for the related data process of importing the students' info from Slate to Blackboard and printing the cards from JSA.

The reason for building this CLI app is that, the automated sync process between systems used by Stevens will not be turned on until the start of every semester. In order to print the Stevens ID card for the newly admitted incoming students in advance, we will need to validate and import the data extracted from Slate to Blackboard. And to do that, I choos Python over Excel, because **Benji is a nerd**.

This program will be shared and maintained among the memebers of DuckCard office, I happy if anyone can help add more functionality and make this app more stable.

## Usage example

### Install the package

1. ```git clone``` this repo in your computer.

> **NOTE**: There is no currently compactibility for Windows OS, next operating system to build is Linux. Windows is a great product, just no taste :-/

2. Under the master branch of repo. Install this local package in the same way you install any other Python package. With a littly bit different on the option you pass to ```pip install```

```sh
$ pip install --editable .
```

> **NOTE**: As I havn't put it on PyPI, you can only install it in this way locally, ```--editable``` option means that whenever you modify the source code and save it, the command-line operation will change along with the modification.

### First time run the command: build the database

Run the following command, and it will take 5-10 minutes to build the database, as the InCampusPersonnel are a lot.

The data source files **MUST BE DOWNLOAD UNDER THE SAME DIRECTORY OF THE REPO**

- structure of the diretories:

```sh
.../SomeFolder
    |- Stevens_DuckcardOffice
    |- DuckCard_data
```

- run the command (any where you want)

```sh
$ duckcard --first-time init
This operation will take about 5 minutes to finish, please do not close the terminal...
```

- after the ```init``` run finished, you can use subcommand ```display``` to see the conclusion of database.

```sh
$ duckcard display
```

- or during the ```init``` you can use option ```--verbose``` or ```-v``` for short to display the conclusion right after buidling finished.

```sh
$ duckcard --first-time init -v
```

### TODO:

Documentation is **NOT** my thing for real. As you have built the database, you can just see the help message by only enter ```duckcard``` command, and check out the source code.

- This will show you the manual

```sh
$ duckcard
```
