# Pype
Pype is an experimental, work-in-progress Python utility that applies simple Python snippets to text files. Its functionality is inspired by Perl's "-p" and "-n" flags, which allow snippets of Perl code to be applied to each line of a text file.

Pype processes text files by splitting them into "records" and executing a given Python snippet for each one. Records, by default, correspond to individual lines of text, but . Information about the current record is stored in a variable called `_`. This variable has attributes containing the record contents (`_.record` or `_.R`), the current file being read (`_.file`), the record number (`_.record_num` or `_.N`), and - if the "-F" flag is used when invoking Pype - a list (`_.fields`) containing text fields split from the record (similar to Perl's "-F" flag). `_` will evaluate to `_.record` when converted to a string implicitly (e.g. `print(_)`) or explicitly (e.g. `str(_)`) as a convenient shorthand.

Defined variables persist between the processing of each record and individual code snippets can be run before or after all lines are processed. This allows one to perform complex behavior without ever having to write a single loop or file open(). 

# Example Usage

### Repeat Each Line of a Text File Three Times
```
$ cat test.txt 
one
two
three
four

$ python3 pype.py -c "print(_.record * 3)" test.txt 
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

$ python3 pype.py -F '\s+' -c 'print(", ".join(_.record_fields))' test.txt 
one, two, three, four
five, six, seven, eight
```

### Pretty-Print a Single Line JSON File
```
$ cat test.json
{"menu": {"id": "file","value": "File","popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"},{"value": "Open", "onclick": "OpenDoc()"},{"value": "Close", "onclick": "CloseDoc()"}]}}}

$ python3 pype.py -i json -i pprint -c "pprint.pprint( json.loads(_.record), compact=True )" test.json
{'menu': {'id': 'file',
          'popup': {'menuitem': [{'onclick': 'CreateNewDoc()', 'value': 'New'},
                                 {'onclick': 'OpenDoc()', 'value': 'Open'},
                                 {'onclick': 'CloseDoc()', 'value': 'Close'}]},
          'value': 'File'}}
```

# To Do
* add paragraph record delimiter mode
