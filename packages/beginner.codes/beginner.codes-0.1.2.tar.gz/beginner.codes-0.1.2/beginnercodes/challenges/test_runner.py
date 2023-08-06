from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
import requests


class ChallengeNotFound(Exception):
    ...


class StatusEnum(Enum):
    SUCCESS = auto()
    FAILED = auto()
    EXCEPTION = auto()


@dataclass()
class Result:
    index: int
    expected: Any
    got: Any = field(default=None)
    status: StatusEnum = field(default=StatusEnum.SUCCESS)


def test(challenge: int, solution_func):
    ### These functions must be protected to ensure no CHEATING happens. ###
    def _get_tests(challenge: int) -> list[dict]:
        response = requests.get(
            f"https://raw.githubusercontent.com/beginner-codes/challenges/main/weekday/test_cases_{challenge}.json"
        )
        if response.status_code == 404:
            raise ChallengeNotFound(f"Challenge {challenge} was not found.")

        return response.json()

    def _run_tests(tests: list[dict], solution_func) -> list[Result]:
        results = []
        for index, test_case in enumerate(tests, start=1):
            result = Result(index, test_case["return"])
            try:
                result.got = solution_func(*test_case["args"])
            except Exception as exp:
                result.status = StatusEnum.EXCEPTION
                result.got = exp
            else:
                if result.got != test_case["return"]:
                    result.status = StatusEnum.FAILED

            results.append(result)

        return results

    def _show_results(challenge: int, results: list[Result], total_tests: int):
        failures = 0
        for result in results:
            if result.status == StatusEnum.FAILED:
                print(
                    f"Test {result.index} failed:  Expected {result.expected}, got {result.got}."
                )
                failures += 1

            elif result.status == StatusEnum.EXCEPTION:
                print(f"Test {result.index} failed:  {result.got!r}")
                failures += 1

        if failures:
            print()

        print(f"---- Challenge {challenge} Results ----")
        print(f"{total_tests - failures} passed, {failures} failed")

        if not failures:
            print("\n**** Great job!!! ****")

    tests = _get_tests(challenge)
    results = _run_tests(tests, solution_func)
    _show_results(challenge, results, len(tests))
