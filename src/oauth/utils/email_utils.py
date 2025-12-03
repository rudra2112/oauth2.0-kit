from datetime import date
from typing import List, Optional, Tuple, Union
import re

import email
import email.message


class EmailUtils:

    @staticmethod
    def build_imap_search_criteria(
        senders: Optional[List[str]],
        receivers: Optional[List[str]] = None,
        since: Optional[Union[date, str]] = None,
        unseen_only: bool = False,
    ) -> str:
        """
        Build an IMAP SEARCH criteria string.

        Args:
            senders (List[str]): list of sender email addresses
            receivers (List[str], optional): list of receiver email addresses
            since (Optional[Union[date, str]]): a date or 'DD-Mon-YYYY' string for SINCE
            unseen_only (bool): if True, include only UNSEEN messages

        Returns:
            str: search criteria string suitable for imap.search(None, criteria)

        Usage:
            criteria = build_imap_search_criteria(
                senders=['user@example.com'],
                receivers=['support@company.com', 'info@company.com'],
                since=date(2024, 1, 1),
                unseen_only=True
            )
            status, messages = imap.search(None, criteria)
        """
        criteria_parts = []

        # 1) UNSEEN filter
        if unseen_only:
            criteria_parts.append("UNSEEN")

        # 2) SINCE date filter
        if since:
            if isinstance(since, date):
                # Format: DD-Mon-YYYY (e.g., "01-Jan-2024")
                since_str = since.strftime("%d-%b-%Y")
            else:
                # Validate date format if string provided
                if not re.match(r"\d{1,2}-[A-Za-z]{3}-\d{4}", str(since)):
                    raise ValueError(
                        f"Date string must be in DD-Mon-YYYY format, got: {since}"
                    )
                since_str = str(since)

            criteria_parts.append(f"SINCE {since_str}")

        # 3) FROM senders filter
        if senders:
            # Filter out empty/None senders
            valid_senders = [s.strip() for s in senders if s and s.strip()]

            if not valid_senders:
                raise ValueError("No valid sender addresses provided")

            if len(valid_senders) == 1:
                # Single sender: FROM "email@example.com"
                criteria_parts.append(f'FROM "{valid_senders[0]}"')
            else:
                # Multiple senders: Build nested OR structure
                # Result: (OR (FROM "a@x.com") (OR (FROM "b@x.com") (FROM "c@x.com")))
                or_expression = f'FROM "{valid_senders[0]}"'

                for sender in valid_senders[1:]:
                    or_expression = f'OR ({or_expression}) (FROM "{sender}")'
                criteria_parts.append(f"({or_expression})")

        # 4) TO receivers filter
        if receivers:
            valid_receivers = [r.strip() for r in receivers if r and r.strip()]
            if not valid_receivers:
                raise ValueError("No valid receiver addresses provided")

            if len(valid_receivers) == 1:
                criteria_parts.append(f'TO "{valid_receivers[0]}"')
            else:
                or_expression = f'TO "{valid_receivers[0]}"'
                for receiver in valid_receivers[1:]:
                    or_expression = f'OR ({or_expression}) (TO "{receiver}")'
                criteria_parts.append(f"({or_expression})")

        # Join all criteria with spaces
        return " ".join(criteria_parts) if criteria_parts else "ALL"

    @staticmethod
    def get_email_content(email_msg: email.message.Message) -> Tuple[str, str]:

        body = ""
        html = ""

        # Get the email content
        if email_msg.is_multipart():
            for part in email_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        body += part.get_payload(decode=True).decode()
                    elif content_type == "text/html":
                        html += part.get_payload(decode=True).decode()
        else:
            content_type = email_msg.get_content_type()
            if content_type == "text/plain":
                body += email_msg.get_payload(decode=True).decode()
            elif content_type == "text/html":
                html += email_msg.get_payload(decode=True).decode()

        # If both body and html are empty, return None
        return body, html
