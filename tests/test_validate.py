import unittest
from pathlib import Path
import json
import yaml
from wilson import wcxf

# -----------------------
# 1. EFT File Tests
# -----------------------
class TestEFTFiles(unittest.TestCase):

    def setUp(self):
        self.eft_files = sorted(
            f for f in Path('.').rglob('*')
            if '.eft.' in f.name.casefold()
        )
        if not self.eft_files:
            self.fail("No EFT files found.")

    def test_eft_files(self):
        """Test that all EFT files load correctly."""
        for file in self.eft_files:
            with self.subTest(file=file.name):
                try:
                    with open(file, 'r') as f:
                        wcxf.EFT.load(f)
                except Exception as e:
                    self.fail(f"EFT loading failed for {file.name}: {e}")


# -----------------------
# 2. Basis File Tests
# -----------------------
class TestMainBasisFiles(unittest.TestCase):

    def setUp(self):
        self.eft_files = sorted(
            f for f in Path('.').rglob('*')
            if '.eft.' in f.name.casefold()
        )
        self.basis_files = sorted(
            f for f in Path('.').glob('*')
            if '.basis.' in f.name.casefold()
        )

        if not self.eft_files:
            self.fail("No EFT files found.")
        if not self.basis_files:
            self.fail("No Basis files found.")

        # Load EFT files before validating Basis files (required for correct Basis validation)
        for file in self.eft_files:
            try:
                with open(file, 'r') as f:
                    wcxf.EFT.load(f)
            except Exception as e:
                self.fail(f"EFT loading failed for {file.name}: {e}")

    def test_basis_files(self):
        """Test that all Basis files in the main folder are valid."""
        for file in self.basis_files:
            with self.subTest(file=file.name):
                try:
                    with open(file, 'r') as f:
                        basis = wcxf.Basis.load(f)
                        basis.validate()
                        print(f"[ OK ]  {file.name}")
                except Exception as e:
                    print(f"[FAIL]  {file.name}: {e}")
                    self.fail(f"Basis validation failed for {file.name}: {e}")

class TestChildBasisFiles(unittest.TestCase):

    def setUp(self):
        self.eft_files = sorted(
            f for f in Path('.').rglob('*')
            if '.eft.' in f.name.casefold()
        )
        self.parent_basis_files = sorted(
            f for f in Path('.').glob('*')
            if '.basis.' in f.name.casefold()
        )
        self.child_basis_files = sorted(
            f for f in Path('child').glob('*')
            if '.basis.' in f.name.casefold()
        )

        if not self.eft_files:
            self.fail("No EFT files found.")
        if not self.parent_basis_files:
            self.fail("No parent Basis files found.")
        if not self.child_basis_files:
            self.skipTest("No child Basis files found.")

        # Load EFT files before validating Basis files (required for correct Basis validation)
        for file in self.eft_files:
            try:
                with open(file, 'r') as f:
                    wcxf.EFT.load(f)
            except Exception as e:
                self.fail(f"EFT loading failed for {file.name}: {e}")

       # Load Parent Basis files before validating Child Basis files
        for file in self.parent_basis_files:
            try:
                with open(file, 'r') as f:
                    wcxf.Basis.load(f)
            except Exception as e:
                self.fail(f"Basis loading failed for {file.name}: {e}")

    def test_child_basis_files(self):
        """Test that all Child Basis files are valid."""
        for file in self.child_basis_files:
            with self.subTest(file=file.name):
                try:
                    with open(file, 'r') as f:
                        basis = wcxf.Basis.load(f)
                        basis.validate()
                        print(f"[ OK ]  {file.name}")
                except Exception as e:
                    print(f"[FAIL]  {file.name}: {e}")
                    self.fail(f"Basis validation failed for {file.name}: {e}")


# -----------------------
# 3. JSON - YAML Consistency Tests
# -----------------------
class TestJSONYAMLConsistency(unittest.TestCase):

    def setUp(self):
        self.json_files = sorted(
            f for f in Path('.').rglob('*')
            if any(ext in f.name.casefold() for ext in ['.eft.', '.basis.'])
            and f.suffix.casefold() == '.json'
        )
        self.yaml_files = sorted(
            f for f in Path('.').rglob('*')
            if any(ext in f.name.casefold() for ext in ['.eft.', '.basis.'])
            and f.suffix.casefold() in {'.yaml', '.yml'}
        )

        self.json_stems = {f.stem.casefold() for f in self.json_files}
        self.yaml_stems = {f.stem.casefold() for f in self.yaml_files}

        if not (self.json_files or self.yaml_files):
            self.fail("No JSON or YAML files found.")

        # Check for duplicate filenames
        json_filenames = [f.stem.casefold() for f in self.json_files]
        yaml_filenames = [f.stem.casefold() for f in self.yaml_files]

        duplicates_json = {name for name in json_filenames if json_filenames.count(name) > 1}
        duplicates_yaml = {name for name in yaml_filenames if yaml_filenames.count(name) > 1}

        if duplicates_json:
            self.fail(f"Duplicate JSON file names found: {duplicates_json}")
        if duplicates_yaml:
            self.fail(f"Duplicate YAML file names found: {duplicates_yaml}")

    def test_json_yaml_consistency(self):
        """Test that corresponding JSON and YAML files are consistent."""

        # Step 1: Detect missing `.json` files
        for yaml_file in self.yaml_files:
            with self.subTest(file=yaml_file.name):
                if yaml_file.stem.casefold() not in self.json_stems:
                    self.fail(f"Missing JSON file for {yaml_file.name}")

        # Step 2: Detect missing `.yaml` files
        for json_file in self.json_files:
            with self.subTest(file=json_file.name):
                if json_file.stem.casefold() not in self.yaml_stems:
                    self.fail(f"Missing YAML file for {json_file.name}")

        # Step 3: Perform content comparison
        for yaml_file in self.yaml_files:
            json_file = next(f for f in self.json_files if f.stem.casefold() == yaml_file.stem.casefold())
            with self.subTest(file=yaml_file.name):
                print(f"Checking consistency: {json_file.name} <--> {yaml_file.name}")
                with open(json_file) as f:
                    json_data = json.load(f)
                with open(yaml_file) as f:
                    yaml_data = yaml.safe_load(f)

                self.assertEqual(json_data, yaml_data, f"Mismatch between {json_file.name} and {yaml_file.name}")


# -----------------------
# Test Execution Order
# -----------------------
def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestEFTFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestMainBasisFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestChildBasisFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONYAMLConsistency))
    return suite


# -----------------------
# Run Tests
# -----------------------
if __name__ == '__main__':
    unittest.main(verbosity=2)
