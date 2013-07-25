#!/bin/bash
# what = pdfs and/or html

for what in $@
do
    emacs -l pub.el --eval "(org-publish-project \"$what\")"
done

