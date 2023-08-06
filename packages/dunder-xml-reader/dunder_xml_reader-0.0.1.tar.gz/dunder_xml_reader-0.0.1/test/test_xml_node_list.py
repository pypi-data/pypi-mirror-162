"""Unit tests for the dunder_xml_reader.xml_node_list module"""
import pytest

from dunder_xml_reader import parse_xml
from dunder_xml_reader.xml_node_list import equal_predicate, like_predicate, startswith_predicate, endswith_predicate, \
    not_equal_predicate, XmlNodeList


def test_equal_predicate_matches():
    # Given
    string1 = 'hey'
    string2 = 'hey'

    # When
    result = equal_predicate(string1, string2)

    # Then
    assert result


def test_equal_predicate_doesnt_match():
    # Given
    string1 = 'hey'
    string2 = 'bub'

    # When
    result = equal_predicate(string1, string2)

    # Then
    assert not result


def test_not_equal_predicate_matches():
    # Given
    string1 = 'hey'
    string2 = 'hey'

    # When
    result = not_equal_predicate(string1, string2)

    # Then
    assert not result


def test_not_equal_predicate_doesnt_match():
    # Given
    string1 = 'hey'
    string2 = 'bub'

    # When
    result = not_equal_predicate(string1, string2)

    # Then
    assert result


def test_like_predicate_matches():
    # Given
    string1 = 'make hey while the sun shines'
    string2 = 'hey'

    # When
    result = like_predicate(string1, string2)

    # Then
    assert result


def test_like_predicate_doesnt_match():
    # Given
    string1 = 'make hay while the sun shines'
    string2 = 'hey'

    # When
    result = like_predicate(string1, string2)

    # Then
    assert not result


def test_startwith_predicate_matches():
    # Given
    string1 = 'make hey while the sun shines'
    string2 = 'make hey'

    # When
    result = startswith_predicate(string1, string2)

    # Then
    assert result


def test_startswith_predicate_doesnt_match():
    # Given
    string1 = 'make hay while the sun shines'
    string2 = 'sun shines'

    # When
    result = startswith_predicate(string1, string2)

    # Then
    assert not result


def test_endswith_predicate_matches():
    # Given
    string1 = 'make hey while the sun shines'
    string2 = 'sun shines'

    # When
    result = endswith_predicate(string1, string2)

    # Then
    assert result


def test_endswith_predicate_doesnt_match():
    # Given
    string1 = 'make hay while the sun shines'
    string2 = 'make hay'

    # When
    result = endswith_predicate(string1, string2)

    # Then
    assert not result


def test_get_item(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = xml_doc.Header.To.Credential[1]

    # Then
    assert result.Identity.text() == 'admin@acme.com'


def test_get_item_out_of_bounds(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    with pytest.raises(IndexError) as exc_info:
        _ = xml_doc.Header.From.Credential[99]

    # Then
    assert exc_info.value.args[0] == "list index out of range"


def test_len(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = len(xml_doc.Header.To.Credential)

    # Then
    assert result == 2


def test_for_loop(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = []
    for credential in xml_doc.Header.To.Credential:
        result.append(credential.Identity.text())

    # Then
    assert result == ['bigadmin@marketplace.org', 'admin@acme.com']


def test_list_comprehensions(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = [x.Identity.text() for x in xml_doc.Header.Sender.Credential if x['domain'] == 'DUNS']

    # Then
    assert len(result) == 1
    assert result[0] == '942888711'


def test_filter(sample_xml_text):
    # Given
    credentials = parse_xml(sample_xml_text).Header.To.Credential

    # When
    result = credentials.filter(lambda n: n['domain'] == 'AribaNetworkUserId').first().Identity.text()

    # Then
    assert result == 'bigadmin@marketplace.org'


def test_filter_prop_none_found(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = xml_doc.Header.To.Credential.filter_prop("domain", "not-there")

    # Then
    assert len(result) == 0


def test_filter_prop_some_found(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = xml_doc.Header.To.Credential.filter_prop("domain", "AribaNetworkUserId")

    # Then
    assert len(result) == 2


def test_filter_text_none_found(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = xml_doc.Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress.Street.filter_text('Suite 3')

    # Then
    assert len(result) == 0


def test_filter_text_some_found(sample_xml_text):
    # Given
    xml_doc = parse_xml(sample_xml_text)

    # When
    result = xml_doc.Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress.Street.filter_text('Suite 2')

    # Then
    assert len(result) == 1


def test_first_empty(sample_xml_text):
    # Given
    address = parse_xml(sample_xml_text).Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress

    # When
    result = address.Street.filter(lambda n: n.text() == 'Suite 3').first()

    # Then
    assert result is None


def test_first_many(sample_xml_text):
    # Given
    address = parse_xml(sample_xml_text).Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress

    # When
    result = address.Street.filter(lambda n: n.text() == 'Suite 2').first()

    # Then
    assert result is not None


def test_last_empty(sample_xml_text):
    # Given
    address = parse_xml(sample_xml_text).Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress

    # When
    result = address.Street.filter(lambda n: n.text() == 'Suite 3').last()

    # Then
    assert result is None


def test_last_many(sample_xml_text):
    # Given
    address = parse_xml(sample_xml_text).Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress

    # When
    result = address.Street.filter(lambda n: n.text() == 'Suite 2').last()

    # Then
    assert result is not None


def test_join_text(sample_xml_text):
    # Given
    address = parse_xml(sample_xml_text).Request.ConfirmationRequest.ConfirmationHeader.Contact.PostalAddress

    # When
    result = address.Street.join_text()

    # Then
    assert result == '432 Lake Drive, Suite 2'


def test_join_prop(sample_xml_text):
    # Given
    credentials = parse_xml(sample_xml_text).Header.To.Credential

    # When
    result = credentials.join_prop('domain')

    # Then
    assert result == 'AribaNetworkUserId, AribaNetworkUserId'


def test_repr_filled(sample_xml_text):
    # Given
    credentials = parse_xml(sample_xml_text).Header.To.Credential

    # When
    result = str(credentials)

    # Then
    assert result == 'XmlNodeList: [Credential]'


def test_repr_empty(sample_xml_text):
    # Given
    credentials = parse_xml(sample_xml_text).Header.To.Credential.filter_prop("domain", "not-here")

    # When
    result = str(credentials)

    # Then
    assert result == 'XmlNodeList: []'


def test_map_attr(sample_xml_text):
    # Given
    from_header = parse_xml(sample_xml_text).Header.To

    # When
    result = [i.text() for i in from_header.Credential.map_attr('Identity')]

    # Then
    assert result == [
        from_header.Credential[0].Identity.text(),
        from_header.Credential[1].Identity.text()
    ]


def test_map_prop(sample_xml_text):
    # Given
    from_header = parse_xml(sample_xml_text).Header.To

    # When
    result = from_header.Credential.map_prop('domain')

    # Then
    assert result == ['AribaNetworkUserId', 'AribaNetworkUserId']


def test_map_text(sample_xml_text):
    # Given
    credentials = parse_xml(sample_xml_text).Header.To.Credential
    cred_identities = XmlNodeList(credentials.map_attr('Identity'))

    # When
    result = cred_identities.map_text()

    # Then
    assert result == ['bigadmin@marketplace.org', 'admin@acme.com']
