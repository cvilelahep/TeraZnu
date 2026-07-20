#!/usr/bin/env python3

import argparse
import gzip
import xml.etree.ElementTree as ET


def remove_elements(parent, tag):
    """Recursively remove all child elements with the given tag."""
    # Remove matching direct children
    for child in list(parent):
        if child.tag == tag:
            parent.remove(child)
        else:
            remove_elements(child, tag)


def main():
    parser = argparse.ArgumentParser(
        description="Remove all XML elements with a given tag from a gzipped XML file."
    )
    parser.add_argument("input_gz", help="Input .xml.gz file")
    parser.add_argument("output_gz", help="Output .xml.gz file")
    parser.add_argument("tag", help="XML tag to remove (e.g. Password)")
    args = parser.parse_args()

    # Read XML from gzip
    with gzip.open(args.input_gz, "rb") as f:
        tree = ET.parse(f)

    root = tree.getroot()

    # Handle the case where the root itself matches
    if root.tag == args.tag:
        raise ValueError("Cannot remove the root element.")

    remove_elements(root, args.tag)

    # Write back to gzip
    with gzip.open(args.output_gz, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=False)


if __name__ == "__main__":
    main()
