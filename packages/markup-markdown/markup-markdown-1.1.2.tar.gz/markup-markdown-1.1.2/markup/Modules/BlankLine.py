# -*- coding: utf-8 -*-
# Copyright 2022 Hai Liang W.
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from markup.Module import Module
from markup.Transform import Transform
import markup.Markers as Markers

class BlankLine(Module):
    """
    Add a blank line marker
    """

    priority = 1.4
    
    def transform(self, data):
        transforms = []
        linenum = 0

        for line in data:
            stripped = line.strip()
            if stripped == Markers.markup_markdown_blank:
                transform = Transform(linenum, "swap", "\n")
                transforms.append(transform)
            linenum = linenum + 1

        return transforms
