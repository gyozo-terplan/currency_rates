import xml.etree.ElementTree as ET

def get_inner_xml(soap_xml):
    """Kibontja az escaped XML-t a SOAP válaszból."""
    root = ET.fromstring(soap_xml)
    for elem in root.iter():
        if "GetExchangeRatesResult" in elem.tag:
            if len(elem) == 0:
                return elem.text
            for child in elem.iter():
                child.tag = child.tag.split('}', 1)[-1] if '}' in child.tag else child.tag
            return ET.tostring(elem[0], encoding="unicode")
    return None

def parse_mnb_rows(inner_xml_str):
    """A nyers belső XML-ből listát készít."""
    if not inner_xml_str or "<Day" not in inner_xml_str:
        return []

    inner_root = ET.fromstring(inner_xml_str)
    extracted_data = []
    for day in inner_root.findall('Day'):
        date_val = day.get('date')
        for rate in day.findall('Rate'):
            extracted_data.append({
                "date": date_val,
                "currency": rate.get('curr'),
                "unit": int(rate.get('unit')),
                "rate_str": rate.text
            })
    return extracted_data