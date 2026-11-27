import argparse
import json
from pathlib import Path
import sys
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from database.connection import init_schema
from database.demo import preparer_demo


class Resultats(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verdicts = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.verdicts.append({'test': test.id(), 'verdict': 'RÉUSSI'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.verdicts.append({'test': test.id(), 'verdict': 'ÉCHOUÉ'})

    def addError(self, test, err):
        super().addError(test, err)
        self.verdicts.append({'test': test.id(), 'verdict': 'ERREUR'})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.verdicts.append({'test': test.id(), 'verdict': 'IGNORÉ', 'raison': reason})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tests de Turisty')
    parser.add_argument('--rapport', action='store_true', help='Actualise docs/Resultats_tests.json')
    args = parser.parse_args()
    init_schema()
    preparer_demo()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'src'))
    resultat = unittest.TextTestRunner(verbosity=2, resultclass=Resultats).run(suite)
    if args.rapport:
        rapport = {'execution': datetime.now().isoformat(timespec='seconds'),
                   'python': sys.version.split()[0], 'nombre': resultat.testsRun,
                   'echecs': len(resultat.failures), 'erreurs': len(resultat.errors),
                   'tests': resultat.verdicts}
        (ROOT / 'docs' / 'Resultats_tests.json').write_text(
            json.dumps(rapport, indent=2, ensure_ascii=False), encoding='utf-8')
    sys.exit(0 if resultat.wasSuccessful() else 1)
