# Pype
Pype is an experimental, work-in-progress Python utility that applies simple Python snippets to text files. Its functionality is inspired by Perl's "-p" and "-n" flags, which allow snippets of Perl code to be applied to each line of a text file.

Pype processes text files one line at a time, executing a given Python snippet for each one. Information about the current line is stored in a variable called `_`. This variable has attributes containing the line contents (`_.line`), the current file being read (`_.file`), the line number (`_.line_num`), and - if the "-F" flag is used when invoking Pype - a tuple (`_.fields`) containing text fields split from the line (similar to Perl's "-F" flag).

Defined variables persist between lines and individual code snippets can be run before or after all lines are processed, allowing for complex behavior without ever having to write a single loop or file open(). 

# Example Usage

### Repeat Each Line of a Text File Three Times
```
$ cat test.txt 
one
two
three
four

$ python3 pype.py -c "print(_.line * 3)" test.txt 
oneoneone
twotwotwo
threethreethree
fourfourfour
```

### Reformat a Space-Delimited File
```
$ cat test.txt 
one two three four
five six  seven     eight

$ python3 pype.py -F '\s+' -c 'print(", ".join(_.line_fields))' test.txt 
one, two, three, four
five, six, seven, eight
```

### Pretty-Print a Single Line JSON File
```
$ cat test.json
{"menu": {"id": "file","value": "File","popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"},{"value": "Open", "onclick": "OpenDoc()"},{"value": "Close", "onclick": "CloseDoc()"}]}}}

$ python3 pype.py -i json -i pprint -c "pprint.pprint( json.loads(_.line), compact=True )" test.json
{'menu': {'id': 'file',
          'popup': {'menuitem': [{'onclick': 'CreateNewDoc()', 'value': 'New'},
                                 {'onclick': 'OpenDoc()', 'value': 'Open'},
                                 {'onclick': 'CloseDoc()', 'value': 'Close'}]},
          'value': 'File'}}
```

# To Do
* Refactor line-delimiter handling
* Re-organize code into standard Python module structure
* Create setup.py for easy installation
