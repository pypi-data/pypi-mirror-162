# pyreutil

**Pyreutil** is a simple command line utiliy to bulk edit filenames or text files using regex.

  - [Getting started](#getting-started)
  - [Usage](#usage)
  - [Commands](#commands)
  - [Examples](#examples)

## Getting started

You can install the package using pip by running the following command:
```sh
$ pip install pyreutil
```

Or for manual installation using the CLI
```sh
$ git clone https://github.com/michsun/pyreutil.git
$ cd pyreutil
$ python setup.py install
```

## Usage

If installed using pip or CLI, you can run the utility using the following command structure.

```sh
$ pyreutil [-f or -t] [path_to_directory_or_file] [arguments...]
```

Otherwise, if downloaded directly, go to the `pyreutil` folder and use the following commands:
```sh
$ python -m pyreutil [-f or -t] [path_to_directory_or_file] [arguments...]
OR
$ python3 -m pyreutil [-f or -t] [path_to_directory_or_file] [arguments...]
```

## Commands

The full list of commands is listed below:

```
usage: pyreutil [-h] [-t TEXTFILES | -f FILENAMES] [-a APPEND] [-af APPEND_FILE] [-c] [-d] [-i]
                [-l LAMBDA_FUNC] [-r REPLACE] [-rf REPLACE_FILE] [-g GROUP] [-rm REMOVE] [-s SEARCH]
                [-si] [-w] [-md]

pyreutil - A python command line utility for searching and modifying files and filenames using regex.

optional arguments:
  -a APPEND, --append APPEND
                        text to append
  -af APPEND_FILE, --append-file APPEND_FILE
                        appends file contents
  -c, --copy            saves changes as a copy of the original directory/file
  -d, --deep            search subdirectories if a directory is given
  -f FILENAMES, --filenames FILENAMES
                        filenames source
  -g GROUP, --group GROUP
                        integer representing the group to replace. Must be used with -s --search
  -h, --help            show this help message and exit
  -i, --inplace         save changes to the existing directory/file
  -l LAMBDA_FUNC, --lambda-func LAMBDA_FUNC
                        code string to execute in a lambda function
  -rm REMOVE, --remove REMOVE
                        removes regex matches
  -md, --remove-md-links
                        removes markdown links and replaces it with the link name
  -w, --remove-whitespaces
                        removes redundant whitespaces (repeat, leading, trailing, and spaces before a
                        period or comma)
  -r REPLACE, --replace REPLACE
                        string to replace searches with. Must be used with -s --search
  -rf REPLACE_FILE, --replace-file REPLACE_FILE
                        file containing contents to replaces regex searches with. Must be used with -s
                        --search
  -s SEARCH, --search SEARCH
                        searches for regex matches
  -si, --silence        silences the output
  -t TEXTFILES, --textfiles TEXTFILES
                        text source
```

If functions are used in conjunction, they are processed in the following order:
   1. Remove
   2. Append/Append file contents
   3. Search and replace with string/file contents/group/lambda function.
   4. Remove redundant whitespaces

## Examples

- **Search and replace - basic**

To search and replace with a string, you can use the following command
```sh
$ pyreutil -f examples/swift -s '-' -r '_' -i
```

![Basic search and replace example](https://raw.githubusercontent.com/michsun/pyreutil/master/media/search-and-replace-basic-example1.png)

- **Search and replace - group**

To search and replace with a regex group, you can use the following command: 
```sh
$ pyreutil -t examples/markdown/game-theory-wiki.md -s "\[([\[]?[^\[^\]]+[\]]?)]\((http[s]?://[^\)]+)\)" -g=1
```

![Search and replace with regex groups](https://raw.githubusercontent.com/michsun/pyreutil/master/media/search-and-replace-group-example1.png)

Alternatively, you can use group capture syntax e.g. `-r='\g<1>'` or `-r=\1`, both of which function the same as `-g=1`.

- **Search and replace - lambda**

You can also use lambda function syntax to make regex substitutes with the `-l` or `--lambda-func` arguments as in the following example.

```sh
$ pyreutil -f examples/swift -s "(_)([a-z])" -l "x.group(2).upper()"
 ```

![Search and replace - lambda function example](https://raw.githubusercontent.com/michsun/pyreutil/master/media/search-and-replace-lambda-example1.png)

Your code should work in the following function: `re.sub(search_str,  lambda x : <lambda_code> , text)`. 

- **Saving changes**

For any modifications, only a preview is shown by default. To save the changes, you can use `-i` to save inplace, or `-c` to save the changes as a copy of the original file. 

When using `-c`, if a single file is given, a copy of the file is made in the original destination. Alternatively, if a directory is given, a copy of the original folder is made with all files copied. Note that all files are included, even files that don't have any regex matches. When used in conjunction with `-d` or `--deep`, the same is applied to all files in subdirectories.

An example using `-d` and `-c` is shown below.

```sh
$ pyreutil -f examples/swift -s "(_)([a-z])" -l "x.group(2).upper()" -dc
 ```

![Search and replace filename with -c and -d example](https://raw.githubusercontent.com/michsun/pyreutil/master/media/saving-changes-example1.png)
