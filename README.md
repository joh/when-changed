## when-changed: run a command when a file is changed


## What is it?

Tired of switching to the shell to test the changes you just made to
your code? Starting to feel like a mindless drone, manually running
pdflatex for the 30th time to see how your resume now looks?

Worry not, when-changed is here to help! Whenever it sees that you have
changed the file, when-changed runs any command you specify.

So to generate your latex resume automatically, you can do this:

```
$ when-changed CV.tex pdflatex CV.tex
```

Sweetness!

## What do I need?

- Python 2.6+
- watchdog


## Installation

```
pip install https://github.com/joh/when-changed/archive/master.zip
```

## Usage

```
when-changed FILE COMMAND...
when-changed FILE [FILE ...] -c COMMAND
```
