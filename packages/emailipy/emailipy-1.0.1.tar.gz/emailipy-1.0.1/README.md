# emailipy

A small library for combining your CSS and HTML into a single email ready HTML file with inline styles. Additionally, it can lint your CSS for email incompatible CSS properties and values.

```
import emailipy

html = u'<div class="test">stuff</div>'
css = ".test { font-size: 14px; }"

emailipy.inline_css(html, css)
>>> u'<div class="test" style="font-size:14px;">stuff</div>'
```

By default the `inline_css` function will strip out css that will not work on all email clients. You can allow all css to slip through with the `strip_unsupported_css` flag set to `False`.

You can also use the css lint function on its own.

```
import emailipy

css = ".test { opacity: 0.8; }"

emailipy.lint_css(css)
>>> ['Invalid Rule: .test { opacity: 0.8; } -- Outlook 2007/10/13 | Outlook 03/Express/Mail | Yahoo! Mail | Google Gmail']
```

## Installation

If you don't need the command line tools, then you can go the usual route and install with `pip`.

```
$ pip install -e git+https://git@github.com/Parsely/emailipy.git#egg=emailipy
```

# Command-line Tools

## Usage

To use it:

```
$ emailipy-lint --help
$ emailipy-inline --help
```

## emailipy-lint

A command line utility for checking css for email incompatibilities.

```
$ emailipy-lint test.css
Invalid Rule: h1 { opacity: 0.8; } -- Outlook 2007/10/13 | Outlook 03/Express/Mail | Yahoo! Mail | Google Gmail
Invalid Rule: div { margin: 12px; } -- Outlook.com
Invalid Rule: .subtext { background: #FF00FF; } -- Outlook 2007/10/13 | Outlook 03/Express/Mail | Outlook.com | Yahoo! Mail | Google Gmail
Invalid Rule: div.subtext ~ div { margin: 18px; } -- Outlook.com
```

## emailipy-inline

A command line utility for inlining css in an html file. Allows you to disable the linter.

```
$ emailipy-inline test.html test.css
<div style="padding: 20px; font-family: serif;">
    <h1 style="font-size: 20px;">Test</h1>
    <div class="subtext" style="padding: 10px; font-size: 8px; font-family: serif;">more text goes here</div>
    <div style="padding: 20px; color: #FF0000; font-family: serif;">some additional body text and maybe numbers</div>
</div>
```

## Installation

You will need to install the command line tools to use them. They can be installed using `pipsi`. If you don't use `pipsi`, you're missing out.
Here are [installation instructions](https://github.com/mitsuhiko/pipsi#readme).

From within the cloned repo run:

```
$ pipsi install .
```
