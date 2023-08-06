# DOTLANG

World's fastest diagram creator.

# How to use

## Execute

### REPL

- make `output` folder in current directory to hold the output image files

- run `python -mdotlang`

- input the `dotlang code` to the REPL

### From other codes

- import the library
`from dotlang import dotlang`

- input the `dotlang code`
`dotlang(dotlang_code, output_dir=dir_name_output, output_file=file_name_output)`

## Quick examples

- To create directional graph from a to b to c.
`a.b.c`

- Change the shape from oval to box for all nodes:
`[shape=box]a.b.c`

- Change the shape from oval to box for node `b` only:
`a.b[shape=box].c`

# Requirements

`pip install yulibrary`
