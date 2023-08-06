# -*- coding: utf-8 -*-
# Copyright 2022 Hai Liang W.
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from markup.Module import Module
from markup.Transform import Transform
import markup.Markers as Markers

office_word_pagebreak_xml= '''```{=openxml}\n <w:p> <w:r> <w:br w:type="page"/> </w:r> </w:p>\n ```\n'''

class WordPageBreak(Module):
    """
    Add a page break for Office Word.
    Convert to word with pandoc -i MARKDOWN_FILE -o FILE.docx
    """

    priority = 1.5
    
    def transform(self, data):
        transforms = []
        linenum = 0

        for line in data:
            stripped = line.strip()
            if stripped == Markers.markup_markdown_pagebreak:
                transform = Transform(linenum, "swap", office_word_pagebreak_xml)
                transforms.append(transform)
            linenum = linenum + 1

        return transforms
