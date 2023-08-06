# dunder_xml_reader #

## Description/Overview ##

The `dunder_xml_reader` package provides classes and functions that aim to make navigating
and extracting data from an XML document easier and more "Pythonic".   All you have to do is
pass a string containing valid XML to the `parse_xml()` function and it will return a Python
object that exposes properties as dictionary keys and child-nodes as attributes.  The
following sample code illustrates.  Consider the following XML:

    <cXML payloadID="1233444-2001@premier.workchairs.com" xml:lang="en-CA" timestamp="2000-10-12T18:41:29-08:00">
        <Header>
            <To>
                <Credential domain="AribaNetworkUserId" type="marketplace">
                    <Identity>bigadmin@marketplace.org</Identity>
                </Credential>
                <Credential domain="AribaNetworkUserId">
                    <Identity>admin@acme.com</Identity>
                </Credential>
            </To>
        </Header>
    </cXML>

It can be easily nagivated with the following Python code:

    >>> with open('order_request.xml') as infile:
    ...     cxml = dunder_xml_reader.parse_xml(infile.read())
    >>>
    >>> print(cxml['payloadID'])
    1233444-2001@premier.workchairs.com
    >>>
    >>> print(cxml.Header.To.Credential[0].Identity.text())
    bigadmin@marketplace.org
    >>>

As you can see, the property `payloadID` is accessed as if it were a dictionary key of the `cxml`
object.  Likewise, the `Header` child node of the cXML document is accessed as if it were an
attribute of the `cxml` object.

The Python object(s) returned by `parse_xml()` use Python _dunder methods_ to fulfill
functionality provided by other Python built-ins:

    >>> # Python's "in" operator
    >>>
    >>> 'payloadID' in cxml
    True
    >>> 'someOtherThing' in cxml
    False
    >>>

    >>> # Python's "hasattr" function
    >>>
    >>> hasattr(cxml, 'Header')
    True
    >> hasattr(cxml, 'Footer')
    False
    >>>

    >>> # Python's "len" function
    >>>
    >>> len(cxml.Header.To.Credential)
    2
    >>>

The Python objects returns by `parse_xml()` have the following methods:

* `tag()` - Returns the XML element tag (i.e. "&lt;cXML&gt;" returns 'cXML')
* `text()` - Returns the text between the tag and it's closer (i.e. "&lt;p&gt;blah&lt;/p&gt;"
  returns 'blah')

Nodes that have siblings with the same element tag (i.e. `Credential` in the above example) are
represented as a `XmlNodeList`, a subclass of Python's built-in `list`.  The `XmlNodeList` class
has a number of extra _convenience_ methods:

* [`first()` - Returns the first item in the list, or if the list is empty, a default value.](#first)
* [`last()` - Returns the last item in the list, or if the list is empty, a default value.](#last)
* [`filter()` - Filters the list items given a lambda expression.](#filter)
* `filter_prop()` - Filter's the list items looking for items that have a property with a given value.
* `filter_text()` - Filter's the list items looking for items that have text with the given value.
* [`map()` - Transforms each item in the list to another given a lambda expression.](#map)
* `map_attr()` - Transforms each item in the list to the value of the item's given attribute.
* `map_prop()` - Transforms each item in the list to the value of the item's given property.
* `map_text()` - Transforms each item in the list to the value of the item's `text()`.
* [`join_text()` - Returns string created by concatenating the `text()` values from each item.](#join_text)
* [`join_prop()` - Returns a string craeted by concatenating the given property value from each item.](#join_prop)


## Installation ##

The easiest way to install dunder_xml_reader is to use `pip`:

    $ pip install dunder-xml-reader


### Some Examples ###

The following are some examples of how you can use the Python objects returns by `parse_xml()`:

#### <a id="dict"></a> Getting property values by dereferencing as a dictionary ####

    >>> cxml = parse_xml(raw_xml_text)
    >>> payload_id = cxml['payloadID']
    >>> print(payload_id)
    1233444-2001@premier.workchairs.com
    >>>

You can even check to see if a property exists using Python's built-in `in` operator

    >>> cxml = parse_xml(raw_xml_text)
    >>> 'payloadID' in cxml
    True
    >>> 'someOtherWeirdThing` in cxml
    False

#### <a id="list"></a> Getting siblings by dereferencing as a list ####

    >>> cxml = parse_xml(raw_xml_text)
    >>> second_credential = cxml.Header.To.Credential[1]
    >>> print(second_credential.Identity.text())
    admin@acme.com
    >>>

A nice side effect of being able to dereference an CxmlNode as a list is that you can for-loop
over CxmlNodes:

    >>> cxml = parse_xml(raw_xml_text)
    >>> for cred in cxml.Header.To.Credential
    ...   print(cred['domain'], cred.Identity.text())
    ...
    AribaNetworkUserId bigadmin@marketplace.org
    AribaNetworkUserId admin@acme.com
    >>>

You can also use the built-in `len()` function with CxmlNodes:

    >>> cxml = parse_xml(raw_xml_text)
    >>> print(len(cxml.Header.To.Credential))
    2
    >>>

#### <a id="tag"></a> Looking up the original element name with the `.tag()` method ####

    >>> request = parse_xml(raw_xml_text).Request.ConfirmationRequest
    >>> print(request.tag())
    ConfirmationRequest
    >>>

#### <a id="text"></a> Getting the inner-text of the element with the `.text()` method ####

    >>> cxml = parse_xml(raw_xml_text)
    >>> node = cxml.Header.From.Credential.Identity
    >>> print(node.text())
    942888711
    >>>

#### <a id="first"></a> Getting the first of a list of siblings with the `.first()` method ####

    >>> cxml = parse_xml(raw_xml_text)
    >>> node = cxml.Header.To.Credential.first()
    >>> print node['type']
    marketplace
    >>>

#### <a id="last"></a> Getting the last of a list of siblings with the `.last()` method ####

    >>> cxml = parse_xml(raw_xml_text)
    >>> print(cxml.Header.To.Credential.last().Identity.text())
    admin@acme.com
    >>>

#### <a id="filter"></a> Filtering nodes with the `.filter()` method ####

    >>> extrinsics = parse_xml(raw_xml_text).Request.OrderRequest.OrderRequestHeader.Extrinsic
    >>> user_nodes = extrinsics.filter(lambda n: n['name'].startswith('User'))
    >>> print(len(user_nodes), len(extrinsics))
    5 12
    >>>

#### Simpler filtering nodes with the `.filter_prop()` method ####

    >>> extrinsics = parse_xml(raw_xml_text).Request.OrderRequest.OrderRequestHeader.Extrinsic
    >>> user_nodes = extrinsics.filter_prop('name', 'User', startswith_predicate)
    >>> print(len(user_nodes), len(extrinsics))
    5 12
    >>>

#### <a id="map"></a> Mapping nodes to something else with a lambda expression ####

    >>> line_item = parse_xml(raw_xml_text).Request.OrderRequest.ItemOut[0]
    >>> taxes = line_item.tax.map(lambda n: float(n.TaxDetail.TaxAmount.text()))
    >>> print(taxes)
    [0.805063025, 0.0, 3.703289915]
    >>>

#### Simpler mapping with the `.map_attr()` method ####

    >>> from_header = parse_xml(raw_xml_text).Header.From
    >>> identity_nodes = from_header.Credential.map_attr('Identity')
    >>> print(identity_nodes[1].text())
    test_customer
    >>>

#### Simpler mapping with the `.map_prop()` method ####

    >>> from_header = parse_xml(raw_xml_text).Header.From
    >>> credential_domains = from_header.Credential.map_prop('domain')
    >>> print(credential_domains)
    ['DUNS', 'CompanyName', 'InteropKey']
    >>>

#### Simpler mapping with the `.map_text()` method ####

    >>> bill_to = parse_xml(raw_xml_text).Request.OrderRequest.OrderRequestHeader.BillTo
    >>> street = bill_to.Address.PostalAddress.Street.map_text()
    >>> print(street)
    ['1242 West Main Street', 'Suite 6a']
    >>>

#### <a id="join_text"></a> String joining with the `.join_text()` method ####

    >>> address = parse_xml(raw_xml).Request.OrderRequest.OrderRequestHeader.BillTo.Address
    >>> print(address.PostalAddress.Street.join_text("\n"))
    1231 West Main Street
    Suite 6a
    >>>

#### <a id="join_prop"></a> String joining with the `.join_prop()` method ####

    >>> cxml = parse_xml(raw_xml_text)
    >>> print(cxml.Header.From.Credential.join_prop('domain'))
    DUNS, CompanyName, InteropKey
    >>>

## Bonus: SafeReference ##

SafeReference is a wrapper that you can wrap a xmlNode instance in (or any other Python object
graph for that matter) that will prevent errors like:

    TypeError: 'NoneType' object is not subscriptable
    AttributeError: 'NoneType' object has no attribute 'blah'

A quick example.  Say you want to issue the following line of code:

    >>> x = cxml.Request.OrderRequest.OrderRequestHeader.BillTo.Address.PostalAddress.City.text()

But, the XML that was parsed in order to create the `cxml` object doesn't have a `BillTo`
element.  You'd expect to get the following exception:

    AttributeError: 'OrderRequestHeader' object has no attribute 'BillTo'

Now you could test your way through the graph heirchy (aka _look-before-you-leap_):

    >>> if hasattr(cxml, 'Request') and \
    ...    hasattr(cxml.Request, 'OrderRequest') and \
    ...    hasattr(cxml.Request.OrderRequest, 'OrderRequestHeader') and \
    ...    hasattr(cxml.Request.OrderRequest.OrderRequestHeader, 'BillTo'):
    ...   x = cxml.Request.OrderRequest.OrderRequestHeader.BillTo.Address.PostalAddress.City.text()
    ... else:
    ...   x = ''

Or, you could just wrap your assignment in a try/except (aka _ask-for-forgiveness_):

    >>> try:
    ...   x = cxml.Request.OrderRequest.OrderRequestHeader.BillTo.Address.PostalAddress.City.text()
    ... except AttributeError:
    ...   x = ''

But in both cases you're writing a lot of "check to see if it's really there"-type code.  The
goal of SafeReference is to prevent that code from needing to be written in the first place.
If your object-graph is wrapped in a SafeReference instance, it will check at each level
for the requested attribute to be there or missing.  If it's there, it will return the
requested attribute.  However, if it's not there, it will return a default-value.  Here's
an example:

    >>> cxml = parse_cxml(raw_xml_text_thats_missing_a_BillTo_element)
    >>> safe_cxml = safe_reference(cxml, 'n/a')
    >>> x = cxml.Request.OrderRequest.OrderRequestHeader.BillTo.Address.PostalAddress.City.text()
    >>> print(x)
    n/a
    >>>

This result of `n/a` will be the result no matter what item is missing (`Request`, `OrderRequest`,
`OrderRequestHeader`, `BillTo`, etc.) along the way.  If any of the objects in that long
dereferencing are missing, the default will be returned.  However, if nothing is missing, the
actual graph value will be returned.

    >>> cxml = parse_cxml(raw_xml_text_with_nothing_missing)
    >>> safe_cxml = safe_reference(cxml, 'n/a')
    >>> x = cxml.Request.OrderRequest.OrderRequestHeader.BillTo.Address.PostalAddress.City.text()
    >>> print(x)
    New York
    >>>
