Utilities and command line for working with EBooks.
Basic support for talking to Apple Books, Calibre, Kindle, Mobi.

*Latest release 20220805*:
* CalibreCommand.books_from_spec: UPPERCASE matches a format.
* CalibreCommand: new cmd_linkto to link book files into an external directory with nice names.
* CalibreTree: fix .fspath and the associated .pathto and format paths.

These form the basis of my personal Kindle and Calibre workflow.

# Release Log



*Release 20220805*:
* CalibreCommand.books_from_spec: UPPERCASE matches a format.
* CalibreCommand: new cmd_linkto to link book files into an external directory with nice names.
* CalibreTree: fix .fspath and the associated .pathto and format paths.

*Release 20220626*:
* CalibreBook: new setter mode for .tags, CalibreCommand: new cmd_tags to update tags.
* CalibreBook.pull_format: AZW formats: also check for AZW4.
* CalibreCommand.books_from_spec: /regexp: search the tags as well.
* CalibreBook: subclass FormatableMixin; CalibreCommand.cmd_ls: new "-o ls_format" option for the top line format.

*Release 20220606*:
Initial PyPI release.
