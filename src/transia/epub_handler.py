"""EPUB extraction, metadata access, spine traversal, and repackaging."""

import os
import shutil
import zipfile
import tempfile
from lxml import etree
from .standalone_utils import logger

class EpubHandler:
    NS = {
        'opf': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    def __init__(self, epub_path):
        self.epub_path = epub_path
        self.temp_dir = tempfile.mkdtemp()
        self.html_files = []

    def extract(self):
        logger.info(f"Extracting EPUB: {self.epub_path}")
        with zipfile.ZipFile(self.epub_path, 'r') as epub:
            epub.extractall(self.temp_dir)

    def get_opf_path(self):
        container_path = os.path.join(self.temp_dir, "META-INF/container.xml")
        tree = etree.parse(container_path)
        return os.path.join(self.temp_dir, tree.xpath("//@full-path")[0])

    def get_metadata(self):
        """Extracts title, author, and description from OPF."""
        opf_path = self.get_opf_path()
        tree = etree.parse(opf_path)
        
        metadata = {
            "title": "Unknown",
            "author": "",
            "description": "",
            "language": ""
        }
        
        title = tree.xpath("//opf:metadata/dc:title/text()", namespaces=self.NS)
        if title:
            metadata["title"] = title[0]
            
        author = tree.xpath("//opf:metadata/dc:creator/text()", namespaces=self.NS)
        if author:
            metadata["author"] = author[0]
            
        description = tree.xpath("//opf:metadata/dc:description/text()", namespaces=self.NS)
        if description:
            metadata["description"] = description[0]

        language = tree.xpath("//opf:metadata/dc:language/text()", namespaces=self.NS)
        if language:
            metadata["language"] = language[0]
            
        return metadata

    def get_html_files(self):
        """Returns list of HTML files in spine order, including TOC files."""
        if self.html_files:
            return self.html_files
        
        opf_path = self.get_opf_path()
        opf_dir = os.path.dirname(opf_path)
        tree = etree.parse(opf_path)
        
        manifest = {}
        toc_files = []
        for item in tree.xpath("//opf:manifest/opf:item", namespaces=self.NS):
            manifest[item.get('id')] = item.get('href')
            # 识别目录文件 (Nav or NCX)
            media_type = item.get('media-type', '')
            properties = item.get('properties', '')
            if 'nav' in properties or 'ncx' in media_type:
                full_path = os.path.normpath(os.path.join(opf_dir, item.get('href')))
                if os.path.exists(full_path):
                    toc_files.append(full_path)
            
        spine = []
        for itemref in tree.xpath("//opf:spine/opf:itemref", namespaces=self.NS):
            idref = itemref.get('idref')
            if idref in manifest:
                href = manifest[idref]
                full_path = os.path.normpath(os.path.join(opf_dir, href))
                spine.append(full_path)
        
        # 将目录文件放在最前面，这样 AI 可以先“预习”目录
        self.html_files = toc_files + spine
        return self.html_files

    def save(self, output_path):
        logger.info(f"Saving EPUB to: {output_path}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            # 1. Mimetype must be first and uncompressed
            epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            
            # 2. Add all other files
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.temp_dir)
                    if rel_path == 'mimetype':
                        continue
                    epub.write(full_path, rel_path)

    def cleanup(self):
        shutil.rmtree(self.temp_dir)
