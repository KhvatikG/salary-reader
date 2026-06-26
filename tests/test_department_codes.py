import unittest

from salary_reader.helpers.iiko_helpers import normalize_department_codes


class NormalizeDepartmentCodesTests(unittest.TestCase):
    def test_none_and_null_state(self):
        self.assertEqual(normalize_department_codes(None), [])
        self.assertEqual(normalize_department_codes("NULL"), [])

    def test_single_string(self):
        self.assertEqual(normalize_department_codes("3"), ["3"])

    def test_list(self):
        self.assertEqual(normalize_department_codes(["1", "2", "3"]), ["1", "2", "3"])

    def test_employee_345_like_payload(self):
        payload = {
            "code": "345",
            "departmentCodes": ["1", "2", "3"],
        }
        self.assertEqual(
            normalize_department_codes(payload["departmentCodes"]),
            ["1", "2", "3"],
        )

    def test_single_department_string_not_split_into_chars_bug(self):
        # "12" must stay one code, not ["1", "2"]
        self.assertEqual(normalize_department_codes("12"), ["12"])


if __name__ == "__main__":
    unittest.main()
