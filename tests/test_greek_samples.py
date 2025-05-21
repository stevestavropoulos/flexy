import unittest, subprocess, json, os

class GreekSamplesTest(unittest.TestCase):
    def test_samples(self):
        path = os.path.join(os.path.dirname(__file__), 'greek_samples.tsv')
        with open(path, encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                line=line.strip()
                if not line:
                    continue
                word, rule, expected_json = line.split('\t')
                expected = set(json.loads(expected_json))
                proc = subprocess.run(['python3','flexy.py','-l','greek', word, rule],
                                     stdout=subprocess.PIPE, check=True)
                got = set(proc.stdout.decode('utf-8').strip().split('\n'))
                self.assertEqual(got, expected, f'mismatch at line {idx}: {word} {rule}')

if __name__ == '__main__':
    unittest.main()
