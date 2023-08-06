import logging
import time
import traceback
import json

# import threading
from .logged_requests import LoggedRequests

from pprint import pformat
from pprint import pprint
from jsoncomparison import Compare

try:
    import settings
except ImportError:
    traceback.print_exc()


class BaseTestCase(object):
    """
BaseTestCase is the superclass for all the backend(Non UI) and frontend(UI) Testcases and Mobile Testcases
@author: Wang Lin
"""

    # TestEngineCaseInput 即 TestEngineCaseInput from github action（ test-engine目前只支持单线程）
    TestEngineCaseInput = {}

    # GlobalData 是全局数据对象（各个不同的thread发起的不同的testase直接共享该数据）
    GlobalData = {}

    priority = None

    def __init__(self):
        self.pprint = pprint
        self.pformat = pformat
        self.logger = logging

        self.requests = LoggedRequests

        self.testcase_id = None

        self.TestEngineCaseInput = BaseTestCase.TestEngineCaseInput

        # TestEngineTestEngineCaseOutput: case由test-engine触发执行结束后call-back时传入的参数（ test-engine目前只支持单线程）
        self.TestEngineCaseOutput = {}

        self.GlobalData = BaseTestCase.GlobalData

        # # todo: 此处用于 构建多线程时 每个线程独立的 TestEngineCaseInput(线程id作为key)
        # print("===================+++++++++++++==========threading.currentThread().ident")
        # print(threading.currentThread().ident)

        # self.CaseData 用于记录 case执行过程中产生的数据（多数情况用于 某个 testcase chain中, 某个Testcase中有调用了 另外一个Testcase.run_test() 则此case 被定义一个 TestcaseChain）
        # eg:
        # from lintest.api_testcase import APITestCase
        # from tests.api.testcase_demo.testcase1 import Testcase1
        # from tests.api.testcase_demo.testcase2 import Testcase2
        #
        # class Testcase3(APITestCase):
        #     tag = 'case3'
        #
        #     def run_test(self):
        #         # 如下调用方式 Testcase1 & Testcase2 的log 不会 被保存到 Testcase3 的log 中
        #         # Testcase1().run_test()
        #         # Testcase2().run_test()
        #         # print(self.CaseData)
        #
        #         # 如下调用方式 Testcase1 & Testcase2 的log  会  被保存到 Testcase3 的log 中
        #
        #         # 比如： TestAdd1.run_test(self)中会设置 username, self.CaseData['username'] = 'lin'
        #         Testcase1.run_test(self)
        #
        #         # TestAdd2.run_test(self)中会设置 password, self.CaseData['password'] = res['password'], 其中 res可能是某个方法或方法的返回值
        #         Testcase2.run_test(self)
        #
        #         # 此时可以在 TestAdd3 直接通过 self.CaseData 获取 对应的 username & password
        #         self.logger.info(self.CaseData)
        #         self.logger.info(self.CaseData['username'])
        #         self.logger.info(self.CaseData['password'])
        #
        #         # login(self.CaseData['username']), self.CaseData['password']))
        self.CaseData = {}

    # now timeout only support integer seconds, default value is 1200 seconds
    timeout = getattr(settings, "TESTCASE_TIMEOUT", 1200)

    def sleep(self, sleep_seconds):
        time.sleep(sleep_seconds)

    def run_test(self):
        """
        this method must be implement by all backend test cases,
        each test case must encapsulate its business logic into a specific method which called run_test():
        def run_test(self):
            ...
        """
        raise NotImplementedError("---subclass: %s must implement this method: run_test(self)!" % self)

    def teardown(self):
        """
        def teardown(self):
            ...
        """
        pass

    def setup(self):
        """
        def teardown(self):
            ...
        """
        pass

    def assert_equals(self, actual_val, expect_val):
        try:
            assert actual_val == expect_val
            self.logger.info("assert actual_val: %s == expect_val: %s  ====== Passed" % (actual_val, expect_val))
        except AssertionError as e:
            e.args += ('expected value is %s' % expect_val, 'actual_val is %s' % actual_val)
            self.logger.info("assert_equals(%s, %s)  ------ Failed" % (actual_val, expect_val))
            raise

    def assert_contains(self, source_val, target_val):
        try:
            if (
                    (type(source_val) == type(target_val)) and
                    (
                            type(source_val) == str or type(source_val) == int or type(source_val) == float
                    )
            ):
                source_val_str = str(source_val)
                target_val_str = str(target_val)
                if source_val_str.__contains__(target_val_str):
                    self.logger.info(
                        "assert_contains => source_val: %s, target_val: %s    => Passed" % (source_val, target_val))
                else:
                    self.logger.error(
                        "assert_contains => source_val: %s, target_val: %s    -------------------------> Failed" % (
                            source_val, target_val))
                    raise RuntimeError(
                        "assert_contains => source_val: %s, target_val: %s    -------------------------> Failed" % (
                            source_val, target_val))
            else:
                self.logger.error(
                    "assert_contains => source_val: %s, target_val: %s     -------------------------> Failed, "
                    "the type of params should be on of [str, int, float] " % (source_val, target_val))
                raise RuntimeError(
                    "assert_contains => source_val: %s, target_val: %s     -------------------------> Failed, "
                    "the type of params should be on of [str, int, float] " % (source_val, target_val))

        except AssertionError as e:
            e.args += ('assert_contains => source_val is %s' % source_val, 'target_val is %s' % target_val)
            self.logger.error(
                "assert_contains => source_val: %s, target_val: %s      -------------------------> Failed" % (
                    source_val, target_val))
            raise RuntimeError(
                "assert_contains => source_val: %s, target_val: %s      -------------------------> Failed" % (
                    source_val, target_val))

    def assert_is_not_none(self, actual_val):
        try:
            assert actual_val is not None
            self.logger.info("assert %s is not None      ====== Passed" % (actual_val))
        except AssertionError as e:
            e.args += ('expected value is not None', 'actual_val is %s' % actual_val)
            self.logger.info("assert_is_not_none(%s)  -- Failed" % (actual_val))
            raise

    def compare_json_and_return_diff(self, expected_json, actual_json, rules=None):
        """
        此方法 比较两个 json 时会忽略结构体内item的顺序,即如下 json1 & json2 会被认为是相同的
        json1 = {
            "name": "lintest",
            "Company": {
                "name": "IKEA",
                "No": 1
            },
            "version": "1.0"
        }
        json2 = {
            "version": "1.0",
            "name": "lintest",
            "Company": {
                "name": "IKEA",
                "No": 1
            }
        }
        """

        self.logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> compare_json: ")
        self.logger.info("------ expected_json: ")
        self.logger.info(self.pformat(expected_json))
        self.logger.info("------ actual_json: ")
        self.logger.info(self.pformat(actual_json))

        if rules:
            self.logger.info("------ rules:")
            self.logger.info(rules)

        diff = Compare(rules=rules).check(expected_json, actual_json)
        self.logger.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< compare_json diff: ")
        self.logger.info(self.pformat(diff))

        # 判断逻辑交给用户，这里直接返回diff
        return diff

    def compare_json_and_assert_equal(self, expected_json, actual_json, rules=None):
        diff = self.compare_json_and_return_diff(expected_json, actual_json, rules)
        self.pprint(diff)
        assert diff == {}

    def compare_json_with_strict_mode(self, expected_json, actual_json):
        """不会忽略json体内Item的顺序, 即: { "name": "lintest", "version": 1.0 } 和 {"version": 1.0, "name": "lintest" } 是不同的, 本质上就是当做字符串来比较"""

        self.logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> compare_json_with_strict_mode: ")
        v1 = json.dumps(expected_json, sort_keys=False)
        v2 = json.dumps(actual_json, sort_keys=False)

        self.logger.info("------ expected_json: ")
        self.logger.info(self.pformat(v1))

        self.logger.info("------ actual_json: ")
        self.logger.info(self.pformat(v2))

        print("------ expected_json: ")
        self.pprint(v1)
        print("------ actual_json: ")
        self.pprint(v2)

        assert v1 == v2

    # def compare_json_with_strict_mode(self, expected_json, actual_json):
    #     """不会忽略json体内Item的顺序, 即: { "name": "lintest", "version": 1.0 } 和 {"version": 1.0, "name": "lintest" } 是不同的"""
    #
    #     self.logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> compare_json_with_strict_mode: ")
    #     self.logger.info("------ expected_json: ")
    #     self.logger.info(self.pformat(expected_json))
    #     self.logger.info("------ actual_json: ")
    #     self.logger.info(self.pformat(actual_json))
    #
    #     # from collections import OrderedDict
    #     # def sorting(item):
    #     #     if isinstance(item, dict):
    #     #         return sorted((key, sorting(values)) for key, values in item.items())
    #     #     if isinstance(item, list):
    #     #         return sorted(sorting(x) for x in item)
    #     #     else:
    #     #         return item
    #     #
    #
    #     diff = self.compare_json_and_return_diff(json.loads(json.dumps(expected_json, sort_keys=False)),
    #                                              json.loads(json.dumps(actual_json, sort_keys=False)))
    #     assert diff == {}
