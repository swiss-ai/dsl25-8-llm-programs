TEMPLATE_GEN_INSTITUTIONS = """Give a few scientific & publishing institutions *and* their abbreviations. Output only one per line. Do not output any other text.

EXAMPLES:
Technische Universiteit Delft
TU Delft
TUD
Elsevier
"""

TEMPLATE_GEN_NAMES = """Generate a few random names. Output only one per line. Do not output any other text.

EXAMPLES:
Michael K. Scottson
Hjalmar Makela
B. Aaronson
"""

TEMPLATE_GEN_PHONES = """Generate a few random telephone numbers. Output only one per line. Do not output any other text.

EXAMPLES:
+1 (555) 787-7890
+41 7 7847 2336
"""

TEMPLATE_GEN_FAXES = """Generate a few fax numbers. Output only one per line. Do not output any other text.

EXAMPLES:
+81 3 6743 5973
+44 20 7946 0958
"""

TEMPLATE_GEN_ADDRESSES = """Generate a few addresses. Output only one per line. Do not output any other text.

EXAMPLES:
4562 Maple Hollow Dr, Springfield, IL 62704
Bahnhofstrasse 45, 8001 Zürich, Switzerland
"""

TEMPLATE_GEN_DATES = """Generate a few random dates from 1990 up to 2030, in various formats. Output only one per line. Do not output any other text.

EXAMPLES:
01/06/1997
13 April 2026
"""

TEMPLATE_GEN_EMAILS = """Generate a few email addresses for the people listed below, who are working at institutions listed below. Output only one per line. Do not output any other text.

NAMES:
{}

INSTITUTIONS:
{}

EXAMPLES:
a.volkova@ciaa.org
jon@gcaar.com
"""

TEMPLATE_GEN_IPS = """Generate a few of IP addresses that look real. Output only one per line. Do not output any other text.

EXAMPLES:
10.1.2.121/16
97.13.1.132
40:c2:ba:45:6b:0b 
"""

TEMPLATE_GEN_DOMAINS = """Generate a few fictional network domain names, for the institutions below. Output only one per line. Do not output any other text.

INSTITUTIONS:
{}

EXAMPLES:
mit.edu
ethz.ch
"""

TEMPLATE_GEN_PRICES = """Generate a few random prices (may be large or small, may or may not include currency). Output only one per line. Do not output any other text.

EXAMPLES:
98
6,531.00
CHF 158
"""

TEMPLATE_GEN_DESCRIPTION = """Generate a description of a hypothetical contract that includes *some* of the information below (verbatim). The contract involves licencing of books and online materials
Output the description only. Do not output any other text.

INFORMATION:
{}

"""

TEMPLATE_GEN_CONTRACT = """Generate an extensive contract based on the data and description below. When needed, copy the information from DATA exactly, verbatim.

DATA:
{}

BEGIN DESCRIPTION

{}

END DESCRIPTION

---

Structure the contract as follows:

1. **Preamble / Recitals**
    - Identifies the parties (e.g. the university and the publisher)
    - States the purpose and background of the agreement

2. **Definitions**
    - Clarifies key terms used in the contract (e.g., “Licensed Materials”, “Authorized Users”, “Open Access”)

3. **Scope of Agreement**
    - What services or materials are being provided (e.g., access to specific journals or databases)
    - May include details about platforms, formats (PDF, XML), or types of access

4. **License Grant / Rights and Restrictions**
    - Outlines what the institution and its members can and cannot do with the content
    - Often includes access rights, archiving rights, interlibrary loan, text/data mining

5. **Authorized Users and Access**
    - Specifies who may use the content (students, faculty, walk-in users, etc.)
    - Defines access methods (IP authentication, Shibboleth, VPN)

6. **Fees and Payment Terms**
    - Subscription or APC (Article Processing Charge) costs
    - Invoicing schedule and payment deadlines

7. **Term and Termination**
    - Duration of the agreement
    - Conditions under which either party can terminate (e.g., breach, non-payment, cancellation clause)

8. **Usage Data and Reporting**
    - Requirements for the publisher to provide COUNTER-compliant usage statistics
    - How data will be shared and analyzed

9. **Warranties and Disclaimers**
    - Assurances about the content's quality or availability
    - Limitations of liability

10. **Confidentiality**
    - How confidential information will be handled (e.g., pricing terms)

11. **Intellectual Property**
    - Confirms the publisher retains copyright
    - Outlines any rights for the institution to archive or reuse content

12. **Open Access Terms (if applicable)**
    - Includes APC discounts, read-and-publish terms, or transformative agreement details

13. **Governing Law and Dispute Resolution**
    - Which country/state’s laws apply
    - How disputes will be resolved (mediation, arbitration, courts)

14. **Force Majeure**
    - Covers events like natural disasters or pandemics that prevent contract fulfillment

15. **Notices**
    - How official communication between parties will be handled (email, post, etc.)

16. **Entire Agreement and Amendments**
    - States this is the full agreement
    - Explains how changes must be made (typically in writing, signed by both parties)

"""
