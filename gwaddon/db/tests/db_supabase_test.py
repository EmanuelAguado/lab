from os import fspath
import unittest
from pathlib import Path
import sys

sys.path.append(fspath(Path(__file__).parent.parent.parent))

from db.db_supabase import (
    delete_user,
    edit_user,
    login,
    get_studio_data,
    set_studio_data,
    add_user,
)


class TestSupabaseCli(unittest.TestCase):
    username = "e.aguado"
    password = "1234"
    new_user_id = None

    @classmethod
    def setUpClass(cls):

        cls.login_info = login(cls.username, cls.password)
        cls.assertIsNotNone(cls.login_info, "Login failed. Please check credentials.")

    def test_login_success(self):
        self.assertEqual(self.login_info["username"], self.username)

    @unittest.expectedFailure
    def test_login_invalid(self):
        username = "invalid_user"
        password = "invalid_password"
        result = login(username, password)

    def test_get_studio_data(self):
        token = self.login_info.get("token")
        result = get_studio_data(token)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    @unittest.expectedFailure
    def test_get_studio_data_invalid(self):
        token = "invalid_token"
        result = get_studio_data(token)
        self.assertIsNone(result)

    def test_set_studio_data(self):
        studio_key = "7b6ed157-d1c9-462d-b3e1-ba3a1c7db831"
        token = self.login_info.get("token")
        data = {"test": 1}
        original_studio_data = get_studio_data(token)
        set_studio_data(studio_key, token, data)
        set_studio_data(studio_key, token, original_studio_data)

    @unittest.expectedFailure
    def test_set_studio_data_invalid(self):
        studio_key = "7b6ed157-d1c9-462d-b3e1-ba3a1c7db831"
        token = self.login_info.get("token")
        data = {"test": 1}
        try:
            set_studio_data(studio_key + "fake", token, data)
            return
        except:
            ...
        try:
            set_studio_data(studio_key, token + "fake", data)
            return
        except:
            ...
        try:
            other_studio_key = "de7e3a9d-727b-4ea1-9871-b5cafc502c4b"
            set_studio_data(other_studio_key, token, data)

        except:
            ...
        raise Exception("success")

    def test_a_add_user(self):
        new_user_data = {
            "username": "new_user_test",
            "role": "user",
            "password_hash": "hash_value",
            "token": "token_test",
        }
        result = add_user(self.login_info["token"], new_user_data)
        TestSupabaseCli.new_user_id = result.get("id")

    @unittest.expectedFailure
    def test_a_add_user_invalid(self):
        new_user_data = {
            "username": "new_user_test",
            "role": "user",
            "password_hash": "hash_value",
            "token": "token_test",
        }
        result = add_user(self.login_info["token"]+"fake", new_user_data)

    def test_b_edit_user(self):
        new_user_data = {"active": False}
        result = edit_user(self.login_info["token"], self.new_user_id, new_user_data)
        self.assertEqual(result.data[0]["active"], False)

    @unittest.expectedFailure
    def test_b_edit_user_invalid(self):
        new_user_data = {"active": False}
        edit_user(self.login_info["token"]+"fake", self.new_user_id, new_user_data)

    def test_c_delete_user(self):
        delete_user(self.login_info["token"], self.new_user_id)

    @unittest.expectedFailure
    def test_c_delete_user_invalid(self):
        delete_user(self.login_info["token"]+"fake", self.new_user_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
