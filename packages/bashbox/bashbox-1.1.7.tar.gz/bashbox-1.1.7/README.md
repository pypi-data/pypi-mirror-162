![bashbox](https://user-images.githubusercontent.com/42397332/162611592-318869d6-db04-41e0-946b-4f2f0bc67e9a.png)

<div align="center">
	<br>
	<img src="https://img.shields.io/github/workflow/status/rackodo/bashbox/Upload%20Python%20Package?label=Package%20Status&style=for-the-badge&logo=python&logoColor=white">
	<img src="https://img.shields.io/github/v/tag/rackodo/bashbox?style=for-the-badge">
	<img src="https://img.shields.io/github/release-date/rackodo/bashbox?style=for-the-badge">
	<img src="https://img.shields.io/github/commit-activity/w/rackodo/bashbox?style=for-the-badge">
	<br><br>
</div>

Bashbox is a textbox package for Python that provides a simple and easy to use system for creating simplistic and professional looking boxes to use in your Python programs.

Bashbox is developed with the intention to make important warnings or errors during runtime easier to see by drawing them in a distinct box that stands out among other output infromation, and includes customization options to allow for further distinction between different errors.

However, Bashbox can also be used as a simple tool for generating a simple box with preset text which may be helpful for displaying important information such as use policies or instructions at the start of a program.

# Table of Contents
- [Installation](#installation)
  * [Using pip](#using-pip)
  * [Using setup.py](#using-setuppy)
- [Usage](#usage)
  * [Basic bashbox](#basic-bashbox)
  * [Multiple columns](#multiple-columns)
  * [Multiple lines](#multiple-lines)
  * [Multiple columns AND multiple lines](#multiple-columns-and-multiple-lines)
  * [Adding a title](#adding-a-title)
  * [Theming a bashbox](#theming-a-bashbox)
    + [Advanced Theming](#advanced-theming)
  * [Everything all together](#everything-all-together)
- [Advanced usage](#advanced-usage)

# Installation
## Using pip
Run `python -m pip install bashbox` in the context of your choice, and Bashbox will be installed into your Python installation's site-packages.
## Using setup.py
Download the latest release's source code and run `python setup.py install` in the root directory.

# Usage
## Basic bashbox

**Input**
```python
from bashbox import bashbox

box = bashbox()
box.setText(0, "This is a Bashbox!")
box.draw()
```

**Output**
```
╔════════════════════╗
║ This is a bashbox! ║
╚════════════════════╝
```

## Multiple columns

**Input**
```python
from bashbox import bashbox

box = bashbox()
box.setColumns(2)
box.setText(0, "Some Text!")
box.setText(1, "Another column of text!")
box.draw()
```

**Output**
```
╔════════════╦═════════════════════════╗
║ Some Text! ║ Another column of text! ║
╚════════════╩═════════════════════════╝
```

**Note**: `setColumns()` has to be called before any uses of `setText()`, as `setColumns()` clears any set text.

## Multiple lines

**Input**
```python
from bashbox import bashbox

box = bashbox()
box.setText(0, "Here's one line.", "Here's another! Wow!")
box.draw()
```

**Output**
```
╔══════════════════════╗
║ Here's one line.     ║
║ Here's another! Wow! ║
╚══════════════════════╝
```

## Multiple columns AND multiple lines

**Input**
```python
from bashbox import bashbox

box = bashbox()

box.setColumns(2)
box.setText(0, "Here's a column with one line.")
box.setText(1, "Here's another column", "with two lines!")
box.draw()
```

**Output**
```
╔════════════════════════════════╦═══════════════════════╗
║ Here's a column with one line. ║ Here's another column ║
║                                ║ with two lines!       ║
╚════════════════════════════════╩═══════════════════════╝
```

## Adding a title

**Input**
```python
from bashbox import bashbox

box = bashbox()
box.setTitle("Look, this is a title!")
box.setText(0, "There's a title up there!")
box.draw()
```

**Output**
```
╔═══════════════════════════╗
║ Look, this is a title!    ║
╠═══════════════════════════╣
║ There's a title up there! ║
╚═══════════════════════════╝
```


## Theming a bashbox

**Input**
```python
from bashbox import bashbox

double = bashbox()
double.setTheme('double')
double.setText(0, "Themed bashbox!")
double.draw()

single = bashbox()
single.setTheme('single')
single.setText(0, "Themed bashbox!")
single.draw()

curved = bashbox()
curved.setTheme('curved')
curved.setText(0, "Themed bashbox!")
curved.draw()

barebone = bashbox()
barebone.setTheme('barebone')
barebone.setText(0, "Themed bashbox!")
barebone.draw()
```
	
**Output**
```
╔═════════════════╗
║ Themed bashbox! ║
╚═════════════════╝
┌─────────────────┐
│ Themed bashbox! │
└─────────────────┘
╭─────────────────╮
│ Themed bashbox! │
╰─────────────────╯
+-----------------+
| Themed bashbox! |
+-----------------+
```

### Advanced Theming

Bashbox themes are stored as `.bsh` files in the themes folder of the package's root, and consist of a list of unicode character codes. The default bashbox theme, `double.bsh`, looks like this. <br> *(The corresponding characters are printed before each code, and do not appear in the file.)*

```
╔ \u2554
╗ \u2557
╚ \u255a
╝ \u255d
═ \u2550
║ \u2551
╦ \u2566
╣ \u2563
╠ \u2560
╩ \u2569
```

You can create and add your own bashbox themes by making a `.bsh` file in the themes folder and following this guideline for your character codes.

```
Top Left Corner
Top Right Corner
Bottom Left Corner
Bottom Right Corner
Horizontal Line
Vertical Line
Horizontal Split Going Down
Vertical Split Going Right
Vertical Split Going Left
Horizontal Split Going Up
```

## Everything all together

**Input**
```python
from bashbox import bashbox

box = bashbox()
box.setColumns(3)
box.setTheme('curved')
box.setTitle("Friends")
box.setText(0, "Bob", "Regina", "Terry")
box.setText(1, "bobtheman@email.com", "regina.disney@email.com", "terrymaster@email.com")
box.setText(2, "+1 (111) 222-3333", "+1 (444) 555-6666", "+1 (777) 888-9999")
box.draw()
```

**Output**
```
╭──────────────────────────────────────────────────────╮
│ Friends                                              │
├────────┬─────────────────────────┬───────────────────┤
│ Bob    │ bobtheman@email.com     │ +1 (111) 222-3333 │
│ Regina │ regina.disney@email.com │ +1 (444) 555-6666 │
│ Terry  │ terrymaster@email.com   │ +1 (777) 888-9999 │
╰────────┴─────────────────────────┴───────────────────╯
```

# Support and Contributions
If you have any suggestions for Bashbox or want to fork Bashbox to improve upon it or add any features, feel free to do so and even make a pull request! I appreciate each and every contribution made.

If you've found a bug, please make an issue so I can work towards fixing it. I am also reachable by email at spicethings9@gmail.com.
