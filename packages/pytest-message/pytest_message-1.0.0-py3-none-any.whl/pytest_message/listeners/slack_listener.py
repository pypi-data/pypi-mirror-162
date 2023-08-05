import dataclasses
import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Optional

from _pytest.reports import TestReport
from slack_sdk import WebClient, errors

from pytest_message.listeners.listiner import Listener

__all__ = ['SlackListener']


@dataclasses.dataclass
class Status:
    total: int
    passed: int
    failed: int
    skipped: int


DIVIDER = {
    "type": "divider"
}

MAX_TEXT_ERROR_SIZE = 1000
SLACK_LISTENER_ERR_CHUNK_SIZE = int(os.getenv("SLACK_LISTENER_ERR_CHUNK_SIZE", 10))


@dataclasses.dataclass
class ErrReportMetadata:
    thread_id: str
    reports: List[dict]


class SlackListener(Listener):
    def __init__(self, token: str, chat: str, *, on_error_add: Optional[str] = None):
        self.state = []
        self._client = self.configure(token)
        self._chat = chat
        self._on_error_add = on_error_add

    @staticmethod
    def configure(token: str) -> WebClient:
        return WebClient(token=token)

    def update(self, data: Any) -> None:
        self.state.append(data)

    def finish(self) -> None:
        title = f'Test report result - {datetime.datetime.now().ctime()}'
        try:
            self._client.chat_postMessage(channel=self._chat, blocks=[self._get_heading_block(title)])
            self._send_error_to_threads()
        except errors.SlackApiError:
            pass

    def _send_error_to_threads(self):
        grouped_err_messages = []
        #  Send all Test metadata messages first, then append to threads
        for func_name, report in self.state:
            status, err = self._get_test_info(report)
            header = self._create_testfunc_header_block(status, func_name)

            header_response = self._client.chat_postMessage(channel=self._chat, blocks=header)
            thread_ts = header_response.data['ts']

            err_blocks = self._prepare_err_report_block(report)
            grouped_err_messages.extend(self._get_thread_report_chunks(err_blocks, thread_ts))
        with ThreadPoolExecutor() as pool:
            pool.map(self._send_err_report_msg, grouped_err_messages)

    def _send_err_report_msg(self, report_thread: ErrReportMetadata) -> None:
        self._client.chat_postMessage(channel=self._chat, blocks=report_thread.reports,
                                      thread_ts=report_thread.thread_id)

    @staticmethod
    def _get_thread_report_chunks(lst: List[dict], thread_id: str) -> List[ErrReportMetadata]:
        #  Split entire list to list of chunks with size SLACK_LISTENER_ERR_CHUNK_SIZE
        chunks = [lst[i:i + SLACK_LISTENER_ERR_CHUNK_SIZE] for i in range(0, len(lst), SLACK_LISTENER_ERR_CHUNK_SIZE)]

        #  wrap chunk with ReportThread metadata class
        return [ErrReportMetadata(thread_id, x) for x in chunks]

    @staticmethod
    def _get_heading_block(heading: str) -> dict:
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": heading
            }
        }

    def _prepare_err_report_block(self, reports: List[TestReport]) -> List[dict]:
        status, err = self._get_test_info(reports)
        return self._create_testfunc_report_blocks(err)

    @staticmethod
    def _get_test_info(reports: List[TestReport]):
        total = len(reports)
        passed = 0
        failed = 0
        skipped = 0
        errors = []

        for report in reports:
            if report.outcome == 'skipped':
                skipped += 1
            elif report.outcome == 'passed':
                passed += 1
            elif report.outcome == 'failed':
                failed += 1
                errors.append(report.longrepr.reprcrash.message)

        return Status(total, passed, failed, skipped), errors

    def _create_testfunc_header_block(self, status: Status, header) -> List[dict]:

        blocks = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{header}*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": self._create_testfunc_status_msg(status)
                    }
                ]
            }
        ]
        if self._on_error_add and (status.failed or status.skipped):
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{self._on_error_add}*"
                    }
                ]

            })

        return blocks

    def _create_testfunc_status_msg(self, status: Status) -> str:
        if status.total == 1:
            if status.failed:
                return ":red_circle: *Failed*"
            if status.passed:
                return ':large_green_circle: *Passed*'
            if status.skipped:
                return ':white_circle: *Skipped*'
        return self._format_parametrized_report(status)

    @staticmethod
    def _format_parametrized_report(status):
        msg = []
        if status.passed:
            msg.append(f':large_green_circle: *Passed*: {status.passed}')
        if status.failed:
            msg.append(f':red_circle: *Failed*: {status.failed}')
        if status.skipped:
            msg.append(f':white_circle: *Skipped*: {status.skipped}')
        return '\n'.join(msg)

    @staticmethod
    def _create_testfunc_report_blocks(errors: List[str]) -> List[dict]:
        """Creates blocks list for error messages"""
        out = []
        for error in errors:
            if len(error) > MAX_TEXT_ERROR_SIZE:
                error = error[:MAX_TEXT_ERROR_SIZE] + "...."

            out.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'```{error}```'
                }
            })
        return out
