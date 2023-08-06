# Clock CLI

A simple time zone converter for the command line. 

## Usage

Input a time (flexibly parsed by [Arrow](https://arrow.readthedocs.io/en/latest/)) and
see the time localized in all your time zones. If a timezone is provided, the input time
is parsed in that time zone. Otherwise, the input time is parsed in your local time.

```
$ clock "2022-08-10 22:00" -t "Asia/Hong_Kong"
Time zone            Local time
-------------------  -----------------------
America/New_York     2022-08-10 10:00 -04:00
America/Los_Angeles  2022-08-10 07:00 -07:00
Asia/Hong_Kong       2022-08-10 22:00 +08:00
```

Add a new time zone using `--add`. When the entered text matches multiple 
[IANA time zones](https://www.iana.org/time-zones), you will be prompted to choose
which you want. 

```
~/Repos/clock % clock 2022 --add sin
Multiple time zones matched '{text}.' Which is correct?
0. Europe/Chisinau
1. Singapore
2. Europe/Helsinki
3. Europe/Busingen
4. Asia/Singapore
> :
```

Clock CLI saves a list of output time zones in `~/.clock`; feel free to edit this list directly. 

```
$ cat ~/.clock
timezones = [ "America/New_York", "America/Los_Angeles", "Asia/Hong_Kong", ]
```

Additional options are provided for output formatting and debugging. 

```
$ clock --help
Usage: clock [OPTIONS] TIME

  Shows a time in multiple time zones.

Options:
  -t, --timezone TEXT  Time zone of input time
  -f, --format TEXT    Output time format
  -d, --debug          Show debug messages
  --add TEXT           Add a time zone
  --help               Show this message and exit.
```

## License

Copyright 2022 Chris Proctor

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
