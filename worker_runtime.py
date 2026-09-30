from __future__ import annotations

from queue import Queue, Empty
from threading import Event, Thread

from classificador_respostas import classify_reply
from logs_db import upsert_case

class VerificationWorker:
    def __init__(self):
        self.queue = Queue()
        self.stop_event = Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = Thread(target=self._run, daemon=True, name="returns-verification-worker")
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def submit(self, message: dict):
        self.queue.put(message)

    def _run(self):
        while not self.stop_event.is_set():
            try:
                message = self.queue.get(timeout=0.5)
            except Empty:
                continue

            result = classify_reply(
                str(message.get("subject") or ""),
                str(message.get("body") or ""),
            )
            case_key = str(message.get("case_key") or message.get("id") or "").strip()
            if case_key:
                upsert_case(case_key, result.status, result.confidence, "MESSAGE", result.reason)
            self.queue.task_done()

worker = VerificationWorker()
