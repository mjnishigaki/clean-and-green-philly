# classes/vac_props_qc.py
import logging as log
from config.psql import conn
from config.config import log_level
from classes.report_utils import send_report_to_slack, email_report

log.basicConfig(level=log_level)


class VacPropsQC:
    def __init__(self, initial_dataset_size: int):
        self.initial_dataset_size = initial_dataset_size
        self.last_dataset_size = self._get_last_dataset_size()
        self.report = ""

    def _get_last_dataset_size(self) -> int:
        """
        Retrieve the size of the last dataset from the Postgres database.
        Returns:
            int: the size of the last dataset or 0 if not found.
        """
        try:
            sql = "SELECT count(*) FROM vacant_properties_end"
            cur = conn.connection.cursor()
            cur.execute(sql)
            last_size = cur.fetchone()[0]
            log.debug(f"Last dataset size: {last_size}")
            return last_size
        except Exception as e:
            log.error("Error retrieving last dataset size: %s", str(e))
            return 0

    def check_size(self):
        """
        Check if the initial dataset size is smaller than the larger of:
        1) 5% smaller than the last dataset size, or
        2) 30,000 records.
        Raise an exception if the check fails.
        """
        if self.last_dataset_size > 0:
            threshold = max(self.last_dataset_size * 0.95, 30000)
            if self.initial_dataset_size < threshold:
                self.report = f"Initial dataset size ({self.initial_dataset_size}) is smaller than the threshold ({threshold}). Last dataset size was {self.last_dataset_size}."
                log.error(self.report)
                self.send_report_to_slack()
                self.email_report()
                raise ValueError(self.report)
        else:
            if self.initial_dataset_size < 30000:
                self.report = f"Initial dataset size ({self.initial_dataset_size}) is smaller than 30,000 records."
                log.error(self.report)
                self.send_report_to_slack()
                self.email_report()
                raise ValueError(self.report)

    def send_report_to_slack(self):
        """
        Post the summary report to the Slack channel if configured.
        """
        send_report_to_slack(self.report, "CAGP Diff Bot")

    def email_report(self):
        """
        Email the summary report if configured.
        """
        email_report(self.report, "Clean & Green Philly: Data size issue report")
