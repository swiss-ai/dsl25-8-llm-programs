TEMPLATE_FILTER_ALL = """
From the provided document identify all substrings containing sensitive information, such as:
- Institution names and abbreviations
- Addresses
- Prices
- Dates and durations
- Names of people
- Phone numbers
- Email addresses
- IP addresses
- Domain names

Ignore [REDACTED]. Note that names may be misspelled. Output only substrings that contain sensitive information, line by line. Please do not output additional text. If no sensitive information is found, output `None`.

An example output might look this:

```
ETH Zuerich
American Biophysica1 Union
ABU
Kasarmenstrasse 77 A/B
4450.00
18.6.02
6 months
Michael K. Fall
+41 7 7847 2336
armstrong@hq.abu.org
121.12.63.3
ethz.ch
```

Now please identify the sensitive information from the following lines:

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The sensitive information is:
```
"""

TEMPLATE_FILTER_INSTITUTIONS = """From the provided document identify all the full names of the participarting institutions, and their abbreviations. Output each institution full name or abbreviation on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
American Biophysica1 Union
ABU
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The institution full names and abbreviations are:
```
"""

TEMPLATE_FILTER_NAMES = """From the provided document identify all names mentioned. Output each name on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
Michael K. Fall
Amitabh Pachchan
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The names are:
```
"""

TEMPLATE_FILTER_PHONES = """From the provided document identify all phone numbers and fax numbers mentioned. Output each number on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
+1 (555) 787-7890
+41 7 7847 2336
+372 5576 2263
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The phone and fax numbers are:
```
"""

TEMPLATE_FILTER_DATES = """From the provided document identify all dates mentioned. Output each one on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
01.06.1997
15 April 2026
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The dates are:
```
"""

TEMPLATE_FILTER_ADDRESSES = """From the provided document identify all addresses mentioned. Output each address on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
4571 Ruble Dr, Springfield, IL 62701
Gloriastrasse 101
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The addresses are:
```
"""

TEMPLATE_FILTER_EMAILS = """From the provided document identify all email addresses mentioned. Output each email address on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
v.petrova@bic.org
bill@coucar.com
```
=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The email addresses are:
```
"""

TEMPLATE_FILTER_PRICES = """From the provided document identify all prices mentioned. Output each price on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
6,700
$120
```
=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The prices are:
```
"""

TEMPLATE_FILTER_IPS = """From the provided document identify all IP addresses mentioned. Output each IP address on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
11.1.1.119
d6:d6:e8:b6:bc:f3 
121.12.63.3
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The IP addresses are:
```
"""

TEMPLATE_FILTER_DOMAINS = """From the provided document identify all domain names mentioned. Output each domain name on a new line. If none are found, output `None`. Please do not output additional text.

For example:
```
stanford.edu
giaa.org
```

=== BEGIN DOCUMENT EXTRACT ===

{extract}

=== END DOCUMENT EXTRACT ===

The domain names are:
```
"""

REDACTION_TEMPLATES = {
    "institutions": TEMPLATE_FILTER_INSTITUTIONS,
    "names": TEMPLATE_FILTER_NAMES,
    "phones": TEMPLATE_FILTER_PHONES,
    "dates": TEMPLATE_FILTER_DATES,
    "addresses": TEMPLATE_FILTER_ADDRESSES,
    "emails": TEMPLATE_FILTER_EMAILS,
    "prices": TEMPLATE_FILTER_PRICES,
    "ips": TEMPLATE_FILTER_IPS,
    "domains": TEMPLATE_FILTER_DOMAINS,
}

