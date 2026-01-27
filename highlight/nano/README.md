# Syntax Highlighting - Nano for Linux

## How to install
- Download the `pyscript.nanorc` file in this repository folder.

- Copy the file to the nano highlight system folder:
```sh
cp pyscript.nanorc /usr/share/nano
```

Or you can include that file into a `.nanorc` file in the working directory:
```sh
nano .nanorc # create new folder or edit the .nanorc file
```

Write this line in the `.nanorc` file:
```nano
include "./pyscript.nanorc"
```