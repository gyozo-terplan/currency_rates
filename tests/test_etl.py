import pytest
from src.transformations import get_inner_xml, parse_mnb_rows

# --- MOCK ADATOK ---
MOCK_SOAP_SUCCESS = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetExchangeRatesResponse xmlns="http://www.mnb.hu/arfolyamok.asmx">
      <GetExchangeRatesResult><MNBRates><Day date="2026-02-20"><Rate unit="1" curr="EUR">390,15</Rate><Rate unit="1" curr="USD">365,40</Rate></Day></MNBRates></GetExchangeRatesResult>
    </GetExchangeRatesResponse>
  </soap:Body>
</soap:Envelope>
"""

MOCK_INNER_XML = "<MNBRates><Day date='2026-02-20'><Rate unit='1' curr='EUR'>390,15</Rate></Day></MNBRates>"

# --- TESZTEK ---

def test_get_inner_xml_extraction():
    """Ellenőrzi, hogy a SOAP burkolóból kijön-e a belső XML tartalom."""
    result = get_inner_xml(MOCK_SOAP_SUCCESS)
    assert result is not None
    assert "<MNBRates>" in result
    assert "390,15" in result

def test_parse_mnb_rows_content():
    """Ellenőrzi, hogy a belső XML-ből helyes Python lista készül-e."""
    rows = parse_mnb_rows(MOCK_INNER_XML)
    
    assert len(rows) == 1
    assert rows[0]['currency'] == 'EUR'
    assert rows[0]['unit'] == 1
    assert rows[0]['rate_str'] == '390,15'

def test_parse_mnb_rows_multiple_currencies():
    """Ellenőrzi több deviza feldolgozását egy napon belül."""
    multi_xml = "<MNBRates><Day date='2026-02-20'><Rate unit='1' curr='EUR'>390</Rate><Rate unit='1' curr='USD'>360</Rate></Day></MNBRates>"
    rows = parse_mnb_rows(multi_xml)
    
    assert len(rows) == 2
    currencies = [r['currency'] for r in rows]
    assert "EUR" in currencies
    assert "USD" in currencies

def test_empty_or_invalid_xml():
    """Szélsőérték teszt: mi történik, ha üres vagy hibás az XML."""
    assert parse_mnb_rows(None) == []
    assert parse_mnb_rows("") == []
    assert parse_mnb_rows("<MNBRates></MNBRates>") == []