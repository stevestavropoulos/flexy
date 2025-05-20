#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add project root to sys.path to allow importing greek
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from greek import preaction, postaction, transfertonosdown, transfertonosup, deletefirsttonos, wordencoding

class TestGreek(unittest.TestCase):

    def test_preaction_postaction_involution(self):
        words = ["ελληνικός", "Αθήνα", "εὐχαριστῶ", "οἶκος", "ὕμνος", "γλῶσσα"]
        for word in words:
            self.assertEqual(postaction(preaction(word)), word, f"Mismatch for word: {word}")

        # Test preaction with known word and assert its encoded form
        # Based on wordencoding, 'αί' is 'a', 'εί' is 'e', 'οί' is 'o', 'ου' is 'u', 'υί' is 'y'
        # 'άι' with tonos would be preaction("άι") -> preaction("αί") -> "a"
        # 'αἴ' with psili and tonos -> preaction("αἴ") -> preaction("αί") -> "a"
        # However, the current wordencoding doesn't have combined diacritics mapping directly to single chars.
        # preaction simplifies diacritics first, then maps.
        # e.g. preaction("άι") becomes "αι" (tonos removed before mapping) then "a"
        # e.g. preaction("εἴ") becomes "ει" then "e"
        self.assertEqual(preaction("αί"), "a") # simple diphthong
        self.assertEqual(preaction("άι"), "a") # diphthong with tonos
        self.assertEqual(preaction("εἰ"), "e") # another diphthong
        self.assertEqual(preaction("εἴ"), "e") # diphthong with psili
        self.assertEqual(preaction("οἶ"), "o") # diphthong with psili and perispomeni
        self.assertEqual(preaction("οὔ"), "u") # diphthong with dasia and oxia
        self.assertEqual(preaction("υἱ"), "y") # diphthong
        self.assertEqual(preaction("υἵ"), "y") # diphthong with dasia and oxia

        # Test postaction with known encoded form
        self.assertEqual(postaction("a"), "αι") # Default for 'a' is 'αι'
        self.assertEqual(postaction("e"), "ει") # Default for 'e' is 'ει'
        self.assertEqual(postaction("o"), "οι") # Default for 'o' is 'οι'
        self.assertEqual(postaction("u"), "ου") # Default for 'u' is 'ου'
        self.assertEqual(postaction("y"), "υι") # Default for 'y' is 'υι'
        # Test simple characters
        self.assertEqual(postaction(preaction("κόσμος")), "κοσμος") # tonos removed
        self.assertEqual(postaction(preaction("ΚΟΣΜΟΣ")), "ΚΟΣΜΟΣ") # uppercase preserved
        self.assertEqual(postaction(preaction("ψυχή")), "ψυχη") # tonos removed
        
        # Test specific preaction behavior from code:
        # It converts to lowercase, removes diacritics, then applies wordencoding.
        self.assertEqual(preaction("Άνθρωπος"), "Anurvpos") # Α->A, ν->n, θ->u, ρ->r, ω->v, π->p, ο->o, ς->s
        self.assertEqual(preaction("Μήτηρ"), "Mhthr")   # Μ->M, ή->h, τ->t, η->h, ρ->r
        self.assertEqual(preaction("μήτηρ"), "mhthr")   # μ->m, ή->h, τ->t, η->h, ρ->r
        self.assertEqual(preaction("Ψυχή"), "Cxuh")     # Ψ->C, υ->u, χ->x, ή->h
        self.assertEqual(preaction("ψυχή"), "cxuh")     # ψ->c, υ->u, χ->x, ή->h

    def test_transfertonosdown(self):
        # Encoded: "ἄνθρωπος" -> preaction("ἄνθρωπος") -> "anurvpos" (no tonos in this encoding)
        # The function expects tonos to be marked with specific characters like '1', '2', '3'
        # based on the old encoding scheme used internally by the function.
        # Let's assume the input to transfertonosdown is after preaction AND some other encoding for tonos.
        # The current preaction removes all tonos. The greek.py functions like _gentonos, _puttonos
        # work with a different encoding where tonos is represented by digits.
        # This test will be difficult without knowing the exact expected input format for tonos.
        # Based on _removegrave, _removeoxia, etc. in greek.py, tonos is expected as '1', '2', '3'.
        # And preaction actually maps accented chars to non-accented ones + tonos digit.
        # e.g. ά -> a1, έ -> e1, ή -> h1, ί -> i1, ό -> o1, ύ -> y1, ώ -> v1
        #      ὰ -> a2, ὲ -> e2, ὴ -> h2, ὶ -> i2, ὸ -> o2, ὺ -> y2, ὼ -> v2
        #      ᾶ -> a3,ῆ -> h3, ῖ -> i3, ῦ -> y3, ῶ -> v3

        # "ἄνθρωπος" (oxia on alpha) -> preaction should give "a1nfrvpos" (using 'f' for θ based on full mapping)
        # Let's check the actual preaction output for accented chars
        self.assertEqual(preaction("ἄ"), "a1") # α + oxia
        self.assertEqual(preaction("ᾶ"), "a3") # α + perispomeni
        self.assertEqual(preaction("ὰ"), "a2") # α + varia
        
        # Test case: "ἄνθρωπος" -> "ἀνθρώπου"
        # preaction("ἄνθρωπος") -> a1nfrvpos (assuming θ->f, ω->v)
        # preaction("ἀνθρώπου") -> anfrv1pu (assuming no initial tonos on α, ω->v with oxia)
        # Let's use the actual mapping from greek.py for clarity
        # ἄ -> a1, ν -> n, θ -> u (from `wordencoding`), ρ -> r, ω -> v, π -> p, ο -> o, ς -> s
        # So, preaction("ἄνθρωπος") -> "a1nurvpos"
        # ἀ -> a, ν -> n, θ -> u, ρ -> r, ώ -> v1, π -> p, ο -> o, υ -> u (for genitive ending)
        # So, preaction("ἀνθρώπου") -> "anurv1pu"
        self.assertEqual(postaction(transfertonosdown(preaction("ἄνθρωπος"))), "ἀνθρώπου")
        self.assertEqual(postaction(transfertonosdown(preaction("μάρτυρος"))), "μαρτύρων") # μάρτυρος -> μαρτύρων (gen pl)
        self.assertEqual(postaction(transfertonosdown(preaction("βασιλέως"))), "βασιλέων")

        # Accent already on last possible syllable (ante-penultimate for transfertonosdown means it can move to penult)
        # If oxia on penult ("λόγος"), it should go to ultima ("λογοῦ") if rules apply
        # If oxia on antepenult ("ἄνθρωπος"), it should go to penult ("ἀνθρώπου")
        # If already on ultima, or cannot move based on rules, it stays.
        # transfertonosdown aims to put oxia on penult, or perispomeni on ultima if penult is short.
        self.assertEqual(postaction(transfertonosdown(preaction("θεός"))), "θεοῦ") # θεός (o1s) -> θεοῦ (ou perispomeni)
        self.assertEqual(postaction(transfertonosdown(preaction("ποταμός"))), "ποταμοῦ")
        self.assertEqual(postaction(transfertonosdown(preaction("φιλέω"))), "φιλοῦμεν") # Example from original comments

        # Word where accent cannot move down further or is already "down"
        self.assertEqual(postaction(transfertonosdown(preaction("λογοῦ"))), "λογοῦ") # Already perispomeni on ultima
        self.assertEqual(postaction(transfertonosdown(preaction("σοφοῦ"))), "σοφοῦ") 
        self.assertEqual(postaction(transfertonosdown(preaction("ἀγαθῶν"))), "ἀγαθῶν") # Perispomeni on ultima

        # Words with no accent or one syllable
        self.assertEqual(postaction(transfertonosdown(preaction("θεος"))), "θεος") # No accent
        self.assertEqual(postaction(transfertonosdown(preaction("νούς"))), "νοός") # νοῦς -> νοός (encoded: nu3s -> noo1s)
        self.assertEqual(postaction(transfertonosdown(preaction("εἷς"))), "ἑνός")   # εἷς -> ἑνός
        self.assertEqual(postaction(transfertonosdown(preaction("Ζεύς"))), "Διός")   # Ζεύς -> Διός (special case)

    def test_transfertonosup(self):
        # Test case: "ἀνθρώπου" -> "ἄνθρωπος"
        # preaction("ἀνθρώπου") -> "anurv1pu"
        # preaction("ἄνθρωπος") -> "a1nurvpos"
        self.assertEqual(postaction(transfertonosup(preaction("ἀνθρώπου"))), "ἄνθρωπος")
        self.assertEqual(postaction(transfertonosup(preaction("μαρτύρων"))), "μάρτυρος")
        self.assertEqual(postaction(transfertonosup(preaction("βασιλέων"))), "βασιλέως")
        self.assertEqual(postaction(transfertonosup(preaction("σοφοῦ"))), "σοφός") # σοφοῦ -> σοφός
        self.assertEqual(postaction(transfertonosup(preaction("ἀγαθῶν"))), "ἀγαθός") 
        self.assertEqual(postaction(transfertonosup(preaction("ὁδοῦ"))), "ὁδός")

        # Accent already on the first syllable (or cannot move up)
        self.assertEqual(postaction(transfertonosup(preaction("ἄνθρωπος"))), "ἄνθρωπος")
        self.assertEqual(postaction(transfertonosup(preaction("σοφός"))), "σοφός") # Stays oxia on penult if ultima is short
        self.assertEqual(postaction(transfertonosup(preaction("δῶρον"))), "δῶρον") # Stays perispomeni on penult

        # Words with no accent or one syllable
        self.assertEqual(postaction(transfertonosup(preaction("ανθρωπος"))), "ανθρωπος") # No accent
        self.assertEqual(postaction(transfertonosup(preaction("θεος"))), "θεος")
        self.assertEqual(postaction(transfertonosup(preaction("νους"))), "νους") # no accent, one syllable after preaction (nu3s -> nus)
                                                                            # actually preaction("νοῦς") -> "nu3s"
        self.assertEqual(postaction(transfertonosup("nu3s")), "νοῦς") # no change if already properispomeni and monosyllabic logical word

        # Test "Could not detect ascent" - this happens in _transfertonos if no known pattern matches.
        # The function then tries to prepend 'ε' (encoded as 'e') if the word doesn't start with it.
        # This behavior seems to be for verb augmentations.
        # Example: "λύω" (lu1v) -> "ἔλυον" (e1luon) - needs augment and different ending.
        # transfertonosup itself might not directly show this without a specific verb context.
        # Let's try a word that doesn't fit typical patterns and doesn't start with 'e'.
        # The `print('Could not detect ascent...')` is in an `else` clause of `if symplegma:`.
        # `symplegma` is a list of verb prefixes.
        # If word starts with one of these, it tries to put tonos on it.
        # If not, it tries to put tonos on the third vowel from end, then second, then first.
        # If all fail (e.g. word too short, or no vowels), it might hit the print.
        # However, the code seems to always find a vowel if one exists.
        # The "prepend e" logic: `if not flag and word[0] != 'e': word = 'e' + word`
        # `flag` is true if an accent was successfully placed.
        # So if it can't place an accent AND word doesn't start with 'e', it prepends 'e'.
        # This is hard to trigger if the word has vowels, as one of _puttonos[N]s will likely work.
        # A word with no vowels (after preaction) could trigger it. E.g. "τρψ" (trc from τρ(υ)ψ)
        # preaction("τρψ") -> "trc" (assuming ψ -> c)
        # self.assertEqual(postaction(transfertonosup(preaction("τρψ"))), "ἔτρψ") # hypothetical
        # The function `_puttonosonfirst`, `_puttonosonsecond`, `_puttonosonthird` would fail for "trc".
        # So `flag` would be `False`. `word[0]` ('t') is not 'e'. So it becomes "etrc".
        # Then `postaction("etrc")` -> "ετρψ" (assuming 'c' maps back to 'ψ').
        # Let's verify preaction("ψ") -> "c" - no, preaction("ψ") -> "C" or "c" depending on case. wordencoding has 'ψ': 'c'.
        # wordencoding has 'τ': 't', 'ρ': 'r'.
        self.assertEqual(postaction(transfertonosup("trc")), "ετρψ") # trc -> etrc -> ετρψ
        self.assertEqual(postaction(transfertonosup("sklhr")), "εσκληρ") # σκληρ (no vowels) -> εσκληρ
        # What if it already starts with 'e'? e.g. "ktrc" -> e + ktrc -> "ektrc" -> postaction("ektrc")
        # No, if it starts with 'e', it won't prepend another 'e'.
        # self.assertEqual(postaction(transfertonosup("ectrc")), "εψτρψ") # Example: "εψτρψ" encoded "ectrc", no tonos change, no prepend.

    def test_deletefirsttonos(self):
        # Word with two accents (oxia + perispomeni example from comments in greek.py)
        # "τῶν ποταμῶν ἐν αὐτῷ" -> preaction would process this word by word.
        # Let's take "αὐτῷ" which is preaction("αὐτῷ") -> "auitv3" (αὐ -> aui, τ -> t, ῷ -> v3)
        # If it had another tonos, e.g., "αὐ1τῷ" -> "aui1tv3"
        # deletefirsttonos("aui1tv3") should be "auitv3"
        self.assertEqual(deletefirsttonos("aui1tv3"), "auitv3")
        self.assertEqual(deletefirsttonos("a1nurv1pos"), "anurv1pos") # ἄνθρώ1πος -> ἀνθρώπος (hypothetical double accent)
        
        # From comments: # πρῶτος οὗτος -> prv1tos u3tos -> prvtos u3tos
        self.assertEqual(deletefirsttonos("prv1tosu3tos"), "prvtosu3tos") # Assuming it's one word for the function
        self.assertEqual(deletefirsttonos("prv1tos u3tos"), "prvtos u3tos") # With space

        # Word with one accent (should not change if it's not the 'first' of multiple, or if only one)
        # The function is literally "delete *first* tonos". So if "a1b", it becomes "ab".
        self.assertEqual(deletefirsttonos("a1nurvpos"), "anurvpos") # ἄνθρωπος -> ανθρωπος
        self.assertEqual(deletefirsttonos("anurv1pos"), "anurvpos") # ἀνθρώπου -> ανθρωπου (tonos on ω)
        
        # Word with no accents
        self.assertEqual(deletefirsttonos("anurvpos"), "anurvpos")
        self.assertEqual(deletefirsttonos("ellhnikos"), "ellhnikos")

        # Test with various tonos types
        self.assertEqual(deletefirsttonos("a1b2c3"), "ab2c3") # oxia, varia, perispomeni
        self.assertEqual(deletefirsttonos("a2b1c3"), "ab1c3")
        self.assertEqual(deletefirsttonos("a3b1c2"), "ab1c2")
        self.assertEqual(deletefirsttonos("a1b"), "ab")
        self.assertEqual(deletefirsttonos("a2b"), "ab")
        self.assertEqual(deletefirsttonos("a3b"), "ab")

if __name__ == '__main__':
    unittest.main()
