# mobileconfig

`mobileconfig` is a python3 module to parse `.mobileconfig` files for better examination.

Usage:

```
Usage: python -m mobileconfig [OPTIONS] DIRECTORY COMMAND [ARGS]...

  Parse .mobileconfig files in a given directory

Options:
  --help  Show this message and exit.

Commands:
  consents       Print all user consents
  extract        Extract the plists into given directory
  payload-types  print a summary of PayloadTypes to either a csv or md file
```

The _extract_ command also gives all values for the keys inside payload-types

For your convenience, a link to the gist of all current profiles:  
https://gist.github.com/yotamolenik/154d612900a2b3ce277226fcaebbb2ca