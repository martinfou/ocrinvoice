#!/usr/bin/env python3

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ocrinvoice.parsers.invoice_parser import InvoiceParser

# RONA invoice text from the OCR output (the new OCR version)
rona_text = """Wty
~
KE XN KKK KK KN LRM AN KKK ARK ARK KKK CRRA KC CHEK
RONA+ Saint-Jean~sur-Riche] ieu
41350
170 rue Moreau
St-Jean-sur-Richelieu J2W 2M4
450-359-4695
X XK EK KKK IE KK KK KEK XK CERR
TTEM ate Prix TOTAL
1 1076.93 1,076.43
Depot #413500151 703500
Portion de taxe: $140.20
S-Total: $1,076.43
TPS : $0.00
TVQ : $0.00
Total: $1,076.43
MasterCard $1,076.43
HComp te xH¥RKHHAKHHHIBIG
#Autor 09258E
Employe:511
RONA Inc.
TPS/TVH # 103039624RT0001
TvQ # 1001939455TQ0001
Echange/rembours. Dans les 90 Jours,
dans l'emballase original, sauf
except., notamment les électroménagers.
Détails en magasin ou au:
rona.ca/fr/retours-et-remboursenents
Interessé par une carriére chez RONA?
Appiiquer en-ligne:
wow. ronainc.ca/fr/carrieres
4416 41350 25 25 7/10/25 18:25
VOUS POURRIEZ GAGNER
- 1000$ en carte cadeau RONA!
Pour participer, répondre au sondage suv
opinion.rona.ca
Code acces: 25441641350191
Dernier jour pour remplir le sondage:
le 20 Juil, 2025
*X82009025441 6%"""


def test_total_extraction():
    parser = InvoiceParser()

    print("Testing total extraction with RONA invoice text (OCR version)...")
    print("=" * 60)

    # Test the new OCR correction method
    lines = [line.strip() for line in rona_text.split("\n")]

    print("Looking for total lines:")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if "total" in line_lower or "mastercard" in line_lower:
            print(f"Line {i}: '{line}'")
            amounts = parser._extract_amounts_with_ocr_correction(line)
            print(f"  Extracted amounts: {amounts}")
            # Debug regex match
            pattern = r"[\$€£¥]?\s*(\d{1,3}(?:,\d{3})*)\s*[٠٫٬\.]\s*(\d{2})"
            matches = re.findall(pattern, line)
            print(f"  Regex matches for pattern: {matches}")

    print("\n" + "=" * 60)
    print("Testing full extract_total method:")
    total = parser.extract_total(rona_text)
    print(f"Extracted total: {total}")

    # Debug: Show all amounts found in the text
    print("\n" + "=" * 60)
    print("All amounts found in text:")
    all_amounts = []
    for i, line in enumerate(lines):
        amounts = parser._extract_amounts_with_ocr_correction(line)
        if amounts:
            print(f"Line {i}: '{line}' -> {amounts}")
            all_amounts.extend(amounts)

    print(f"\nAll unique amounts: {list(set(all_amounts))}")

    # Debug: Show what happens in the $1000-$2000 range logic
    print("\n" + "=" * 60)
    print("Debugging $1000-$2000 range logic:")
    float_amounts = []
    for amount_str in all_amounts:
        try:
            cleaned = (
                amount_str.replace("$", "")
                .replace(",", "")
                .replace("€", "")
                .replace("£", "")
                .replace("¥", "")
            )
            value = float(cleaned)
            if 10 <= value <= 10000:
                float_amounts.append(value)
        except (ValueError, TypeError):
            continue

    print(f"All amounts in 10-10000 range: {float_amounts}")
    in_range = [v for v in float_amounts if 1000 <= v <= 2000]
    print(f"Amounts in 1000-2000 range: {in_range}")
    if in_range:
        print(f"Max in range: {max(in_range)}")

    # Debug the problematic line specifically
    print("\n" + "=" * 60)
    print("Debugging problematic line '1 1076.93 1,076.43':")
    problematic_line = "1 1076.93 1,076.43"
    amounts = parser._extract_amounts_with_ocr_correction(problematic_line)
    print(f"Line: '{problematic_line}'")
    print(f"Extracted amounts: {amounts}")

    # Test each amount conversion
    for amount_str in amounts:
        try:
            cleaned = (
                amount_str.replace("$", "")
                .replace(",", "")
                .replace("€", "")
                .replace("£", "")
                .replace("¥", "")
            )
            value = float(cleaned)
            print(f"  '{amount_str}' -> cleaned: '{cleaned}' -> float: {value}")
        except (ValueError, TypeError) as e:
            print(f"  '{amount_str}' -> ERROR: {e}")


if __name__ == "__main__":
    test_total_extraction()
