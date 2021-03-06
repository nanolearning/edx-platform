# -*- coding: utf-8 -*-
"""Test for Image Annotation Xmodule functional logic."""

import unittest
from mock import Mock
from lxml import etree

from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds

from xmodule.imageannotation_module import ImageAnnotationModule

from . import get_test_system


class ImageAnnotationModuleTestCase(unittest.TestCase):
    ''' Image Annotation Module Test Case '''
    sample_xml = '''
        <annotatable>
            <instructions><p>Image Test Instructions.</p></instructions>
            <json>
                navigatorSizeRatio: 0.25,
                wrapHorizontal:     false,
                showNavigator: true,
                navigatorPosition: "BOTTOM_LEFT",
                showNavigationControl: true,
                tileSources:   [{
                    Image:  {
                        xmlns: "http://schemas.microsoft.com/deepzoom/2009",
                        Url: "http://static.seadragon.com/content/misc/milwaukee_files/",
                        TileSize: "254",
                        Overlap: "1",
                        Format: "jpg",
                        ServerFormat: "Default",
                        Size: {
                            Width: "15497",
                            Height: "5378"
                        }
                    }
                },],
            </json>
        </annotatable>
    '''

    def setUp(self):
        """
            Makes sure that the Module is declared and mocked with the sample xml above.
        """
        self.mod = ImageAnnotationModule(
            Mock(),
            get_test_system(),
            DictFieldData({'data': self.sample_xml}),
            ScopeIds(None, None, None, None)
        )

    def test_extract_instructions(self):
        """
        Tests to make sure that the instructions are correctly pulled from the sample xml above.
        It also makes sure that if no instructions exist, that it does in fact return nothing.
        """
        xmltree = etree.fromstring(self.sample_xml)

        expected_xml = u"<div><p>Image Test Instructions.</p></div>"
        actual_xml = self.mod._extract_instructions(xmltree)  # pylint: disable=protected-access
        self.assertIsNotNone(actual_xml)
        self.assertEqual(expected_xml.strip(), actual_xml.strip())

        xmltree = etree.fromstring('<annotatable>foo</annotatable>')
        actual = self.mod._extract_instructions(xmltree)  # pylint: disable=protected-access
        self.assertIsNone(actual)

    def test_get_html(self):
        """
        Tests the function that passes in all the information in the context that will be used in templates/textannotation.html
        """
        context = self.mod.get_html()
        for key in ['display_name', 'instructions_html', 'annotation_storage', 'token', 'tag', 'openseadragonjson']:
            self.assertIn(key, context)
