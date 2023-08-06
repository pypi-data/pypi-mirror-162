# Family parkrun Summary

To use:

- Ensure you have [Python][] installed.
- Create a file containing a newline-separated list of runner ID numbers.
  These are the numbers at the end of the URL for their personal page.
- Run `family-parkrun` with the `-d` argument, followed by the filename
  of your runner list, and wait for it to download.
  ```bash
  python family-parkrun -d runners.txt
  ```
- View `summary.html` in your browser.

[python]: https://www.python.org
