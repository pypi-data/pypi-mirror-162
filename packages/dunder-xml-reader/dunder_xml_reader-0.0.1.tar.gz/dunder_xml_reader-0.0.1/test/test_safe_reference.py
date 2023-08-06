"""Unit tests for the safe_get module"""

import pytest

from dunder_xml_reader import parse_xml, safe_reference


@pytest.fixture
def xml_doc(sample_xml_text):
    return parse_xml(sample_xml_text)


@pytest.fixture
def sut(xml_doc):
    # Given
    return safe_reference(xml_doc, 'isnt-there')


def test_passes_prop_dereference_successfully(sut):
    # When
    result = sut['timestamp']

    # Then
    assert result == '2000-10-12T18:41:29-08:00'


def test_passes_prop_dereference_unsuccessfully_gracefully(sut, mocker):
    # When
    mocker.patch('sys.stderr')
    result = sut['x-version']

    # Then
    assert result == 'isnt-there'


def test_passes_index_deference_successfully(sut):
    # When
    result = sut[0]

    # Then
    assert result == sut


def test_passes_index_deference_unsuccessfully_gracefully(sut, mocker):
    # When
    mocker.patch('sys.stderr')
    result = sut[1]

    # Then
    assert result == 'isnt-there'


def test_passes_attribute_dereference_successfully(sut):
    # When
    result = sut.Header.To.Credential.first().Identity.tag()

    # Then
    assert result == 'Identity'


def test_passes_attribute_dereference_unsuccessfully_gracefully(sut, mocker):
    # When
    mocker.patch('sys.stderr')
    result = sut.Footer.From.Credential.first().Identity.tag()

    # Then
    assert result == 'isnt-there'


def test_passes_len_dereference_successfully(sut):
    # When
    result = len(sut.Header.To.Credential)

    # Then
    assert result == 2


def test_passes_len_dereference_unsuccessfully_gracefully(sut, mocker):
    # When
    mocker.patch('sys.stderr')
    result = len(sut.Footer.From.Credential)

    # Then
    assert result == 10  # *Note: 10 is correct because it's the string length of the default: 'isnt-there'


def test_passes_repr_dereference_successfully(sut):
    # When
    result = str(sut.Header.From)

    # Then
    assert result == 'XmlNode: From'


def test_passes_repr_dereference_unsuccessfully_gracefully(sut, mocker):
    # When
    mocker.patch('sys.stderr')
    result = str(sut.Footer.From.Credential)

    # Then
    assert result == 'isnt-there'


def test_passes_bool_dereference_successfully_true(sut):
    # When
    result = bool(sut.Header.From.Credential[0].Identity.text())

    # Then
    assert result


def test_passes_bool_dereference_successfully_false():
    # Given
    sut = safe_reference(0)

    # When
    result = bool(sut)

    # Then
    assert not result


def test_passes_bool_dereference_unsuccessfully_gracefully(sut, mocker):
    # When
    mocker.patch('sys.stderr')
    result = bool(sut.Footer.From.Credential[0].Identity.text())

    # Then
    assert result # Still is True because the default evaluates to True.
