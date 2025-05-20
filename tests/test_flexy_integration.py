#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import sys
import os

# Ensure run.sh is executable: chmod +x run.sh

class TestFlexyIntegration(unittest.TestCase):

    def run_flexy(self, args_list):
        """
        Helper method to run the run.sh script with given arguments.
        Returns a tuple (stdout, stderr, returncode).
        """
        # Assuming run.sh is in the parent directory of this test file (i.e., project root)
        script_path = os.path.join(os.path.dirname(__file__), '..', 'run.sh')
        
        # Ensure run.sh is executable before running
        # In a real CI/CD environment, this would be part of the setup
        try:
            subprocess.run(['chmod', '+x', script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to make run.sh executable: {e}", file=sys.stderr)
            # Depending on policy, might want to raise an error or skip tests
            pass # For now, we'll let it try to run anyway

        command = ['sh', script_path] + args_list
        
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        return process.stdout, process.stderr, process.returncode

    def test_list_rules(self):
        """Test listing all available rules."""
        stdout, stderr, returncode = self.run_flexy(['--list-rules'])
        
        self.assertEqual(returncode, 0, f"run.sh exited with {returncode}. Stderr: {stderr}")
        self.assertEqual(stderr.strip(), "", f"Stderr should be empty. Got: {stderr}")
        self.assertTrue(len(stdout) > 0, "Stdout should not be empty when listing rules.")
        
        # Check for some known rule names (these are keys from the `kath` dictionary in greek.py)
        self.assertIn("O1 ", stdout) # Space to avoid matching O10, O11 etc.
        self.assertIn("E1 ", stdout)
        self.assertIn("P1 ", stdout)
        self.assertIn("K1 ", stdout)
        self.assertIn("O25 ", stdout) # γυναίκα example rule

    def test_word_and_rule_gynaika_O25(self):
        """Test a specific word 'γυναίκα' with rule 'O25'."""
        word = "γυναίκα"
        rule_id = "O25"
        stdout, stderr, returncode = self.run_flexy([word, rule_id])

        self.assertEqual(returncode, 0, f"run.sh exited with {returncode} for {word} {rule_id}. Stderr: {stderr}")
        self.assertEqual(stderr.strip(), "", f"Stderr should be empty. Got: {stderr}")

        expected_lines = [
            f"{word} OusEnOnom {word} {rule_id}",
            f"γυναίκας OusEnGen {word} {rule_id}",
            f"γυναίκα OusEnAit {word} {rule_id}", # Acc Sg is γυναίκα
            f"γυναίκα OusEnKlit {word} {rule_id}", # Voc Sg is γυναίκα
            f"γυναίκες OusPlOnom {word} {rule_id}",
            f"γυναικών OusPlGen {word} {rule_id}",
            f"γυναίκες OusPlAit {word} {rule_id}",
            f"γυναίκες OusPlKlit {word} {rule_id}",
        ]
        
        # Normalize stdout newlines and remove trailing spaces
        actual_lines = [line.strip() for line in stdout.strip().split('\n')]

        for expected_line in expected_lines:
            self.assertIn(expected_line.strip(), actual_lines, f"Expected line '{expected_line}' not found in output for {word} {rule_id}")

    def test_word_and_rule_anthrwpos_O18(self):
        """Test a specific word 'ἄνθρωπος' with rule 'O18'."""
        word = "ἄνθρωπος" # Note: run.sh handles preaction via iconv and greek.py
        rule_id = "O18" # O18 is for ἄνθρωπος, λόγος type nouns
        
        # Expected forms for ἄνθρωπος (O declension, oxytone like θεός, but O18 is paroxytone like λόγος)
        # O18 is for -ος, -ου (ουδ.) e.g. "το ξίφος"
        # Let's use "λόγος" and its corresponding rule if O18 is not for ἄνθρωπος.
        # From greek.py, O18 is ('ος', ('ου', 'εος'), 'ον', 'ος', 'ου', 'οι', 'ων', 'ους', 'οι', 'η')
        # This seems to be for neuters like "ξίφος, ξίφεος/ξίφους, ξίφος, ξίφος..."
        # Let's pick a more suitable masculine noun or verify O18.
        # The comment "O declension, second, oxytone" -> θεός (O1)
        # "O declension, second, paroxytone" -> λόγος (O2)
        # "O declension, second, proparoxytone" -> ἄνθρωπος (O3)

        word = "ἄνθρωπος"
        rule_id = "O3" # O3 for proparoxytone masculine nouns like ἄνθρωπος
        stdout, stderr, returncode = self.run_flexy([word, rule_id])

        self.assertEqual(returncode, 0, f"run.sh exited with {returncode} for {word} {rule_id}. Stderr: {stderr}")
        # Allow specific warning for proparoxytones if it occurs
        # Example warning: "Warning: proparoxytone with short ultima doesn't get perispomeni in gen/dat -> anurvpou not anurvpo~u"
        # This warning is specific to the internal logic of `accentuate` in `greek.py`.
        # For now, let's assume stderr should be clean unless we are testing this specific warning.
        if "Warning: proparoxytone" not in stderr:
             self.assertEqual(stderr.strip(), "", f"Stderr should be empty or a known warning. Got: {stderr}")


        expected_lines = [
            # Based on preaction("ἄνθρωπος") -> "a1nurvpos"
            # and postaction for each form.
            # The output from run.sh will be in Greek characters.
            f"ἄνθρωπος OmsEnOnom {word} {rule_id}",
            f"ἀνθρώπου OmsEnGen {word} {rule_id}",
            f"ἄνθρωπον OmsEnAit {word} {rule_id}",
            f"ἄνθρωπε OmsEnKlit {word} {rule_id}",
            f"ἄνθρωποι OmsPlOnom {word} {rule_id}",
            f"ἀνθρώπων OmsPlGen {word} {rule_id}",
            f"ἀνθρώπους OmsPlAit {word} {rule_id}",
            f"ἄνθρωποι OmsPlKlit {word} {rule_id}",
        ]
        actual_lines = [line.strip() for line in stdout.strip().split('\n')]
        for expected_line in expected_lines:
            self.assertIn(expected_line.strip(), actual_lines, f"Expected line '{expected_line}' not found in output for {word} {rule_id}.\nActual output:\n{stdout}")

    def test_word_all_rules(self):
        """Test a simple word with all rules applied."""
        word = "λόγος"
        stdout, stderr, returncode = self.run_flexy([word])
        
        self.assertEqual(returncode, 0, f"run.sh exited with {returncode} for {word} (all rules). Stderr: {stderr}")
        self.assertEqual(stderr.strip(), "", f"Stderr should be empty. Got: {stderr}")
        self.assertTrue(len(stdout) > 0, "Stdout should not be empty when applying all rules.")
        
        # Check if multiple rules were applied by looking for different rule IDs in output
        # Example: O2 (for λόγος itself), and some others it might match partially
        self.assertIn(f"{word} O2", stdout) # Check for the primary rule output
        self.assertTrue(stdout.count('\n') > 8, "Expected more than 8 lines of output for all rules on 'λόγος'")
        # Check that it tried to apply other categories, e.g. from Adjectives (A) or Verbs (K)
        # This is a loose check, just to see if it's trying various things.
        self.assertTrue(any(f" {cat}" in line for line in stdout.split('\n') for cat in [" A", " K", " P", " E"]),
                        "Expected output to show attempts from different rule categories.")

    def test_invalid_rule_id(self):
        """Test with a non-existent rule ID."""
        word = "λόγος"
        invalid_rule_id = "XYZ123"
        stdout, stderr, returncode = self.run_flexy([word, invalid_rule_id])
        
        # flexy.py is expected to exit with 0 even if a rule is not found,
        # but it prints a message to stderr.
        self.assertEqual(returncode, 0, f"run.sh exited with {returncode} (expected 0). Stderr: {stderr}")
        self.assertIn(f"I don't know how to do technique {invalid_rule_id}", stderr)
        self.assertEqual(stdout.strip(), "", "Stdout should be empty for an invalid rule ID.")

    def test_run_sh_no_args(self):
        """Test run.sh with no arguments (should print help)."""
        stdout, stderr, returncode = self.run_flexy([])
        self.assertEqual(returncode, 0, f"run.sh with no args exited with {returncode}. Stderr: {stderr}")
        self.assertIn("Usage: run.sh [--list-rules] [word [ruleid]]", stdout)

    def test_run_sh_help_argument(self):
        """Test run.sh with --help argument."""
        stdout, stderr, returncode = self.run_flexy(['--help'])
        self.assertEqual(returncode, 0, f"run.sh --help exited with {returncode}. Stderr: {stderr}")
        self.assertIn("Usage: run.sh [--list-rules] [word [ruleid]]", stdout)


if __name__ == '__main__':
    # This allows running the tests directly
    # It's good practice to ensure run.sh is executable from here too, or before running.
    # For example, one might run: chmod +x ./run.sh && python -m unittest tests.test_flexy_integration
    unittest.main()
