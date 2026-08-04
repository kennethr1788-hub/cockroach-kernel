from __future__ import annotations

import unittest

import live_lambda_handler


class LiveLambdaEntrypointTests(unittest.TestCase):
    def test_entrypoint_delegates_without_adding_authority(self):
        sentinel = {"statusCode": 200, "body": "{}"}
        original = live_lambda_handler._handler
        calls = []
        try:
            live_lambda_handler._handler = lambda event, context: calls.append(
                (event, context)
            ) or sentinel
            event = {"rawPath": "/demo/promote"}
            self.assertIs(live_lambda_handler.lambda_handler(event, "ctx"), sentinel)
            self.assertEqual(calls, [(event, "ctx")])
        finally:
            live_lambda_handler._handler = original


if __name__ == "__main__":
    unittest.main()
