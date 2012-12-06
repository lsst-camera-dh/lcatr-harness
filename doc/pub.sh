#!/bin/bash
for what in $@
do
    emacs --batch -l pub.el --eval "(org-publish-project \"$what\")"
done

