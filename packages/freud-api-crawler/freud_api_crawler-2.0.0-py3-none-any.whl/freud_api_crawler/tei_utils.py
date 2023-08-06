import lxml.etree as ET


def make_pb(json):
    """ returns a tei:pb
    """
    pb_el = ET.Element("{http://www.tei-c.org/ns/1.0}pb")
    pb_el.attrib['n'] = f"{json['page_nr']}"
    pb_el.attrib[
        "{http://www.w3.org/XML/1998/namespace}id"
    ] = f"page__{json['id']}"

    return pb_el
