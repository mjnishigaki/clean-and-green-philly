# classes/report_utils.py

import logging as log
import os
import smtplib
from email.mime.text import MIMEText
from slack_sdk import WebClient
from config.config import (
    from_email,
    smtp_server,
    report_to_email,
    report_to_slack_channel,
)

log.basicConfig(level=log.INFO)


def send_report_to_slack(report: str, bot_name: str = "CAGP Diff Bot"):
    """
    Post the summary report to the Slack channel if configured.

    Args:
        report (str): The report message to be sent.
        bot_name (str): The name of the bot to be displayed in Slack. Defaults to "CAGP Diff Bot".
    """
    if report_to_slack_channel:
        token = os.environ["CAGP_SLACK_API_TOKEN"]
        client = WebClient(token=token)

        # Send a message
        client.chat_postMessage(
            channel=report_to_slack_channel,
            text=report,
            username=bot_name,
        )


def email_report(report: str, subject: str):
    """
    Email the summary report if configured.

    Args:
        report (str): The report message to be emailed.
        subject (str): The subject of the email.
    """
    if report_to_email:
        # Create a text/plain message
        msg = MIMEText(report)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = report_to_email

        # Send the message via our own SMTP server
        s = smtplib.SMTP(smtp_server)
        s.sendmail(from_email, [report_to_email], msg.as_string())
        s.quit()
