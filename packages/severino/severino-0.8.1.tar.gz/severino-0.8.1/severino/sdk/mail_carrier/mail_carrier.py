import base64
import os
import tempfile
import uuid
import webbrowser

from jinja2 import BaseLoader, Environment

from severino.sdk.helpers.http_requests import Http
from severino.settings import SEVERINO_API_URL


class MailCarrier:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/mail-carrier"

    def last_email_sent_to(self, email: str):
        return self.http.get(
            url=f"{self.severino_api_url}{self.path}/last-email-sent-to/{email}/"
        )

    def send(
        self,
        from_connection: uuid,
        template_name: str,
        to_email: list,
        bcc: list = None,
        cc: list = None,
        reply_to: list = None,
        subject: str = "",
        context_vars: dict = {},
        files: list = [],
    ):
        """Send emails using Severino.

        Args:
            from_connection (uuid): UUID that identifies the connection (credentials) that will be used to send the email.
            template_name (str): Name of the template to be used for sending the email.
            to_email (list): A list of recipient addresses. Recipients are the audience of the message.
            bcc (list, optional): A list of addresses used in the “Bcc” header when sending the email. Recipients are those being discreetly or surreptitiously informed of the communication and cannot be seen by any of the other addressees. P.s: It is common practice to use the BCC: field when addressing a very long list of recipients, or a list of recipients that should not (necessarily) know each other, e.g. in mailing lists.
            cc (list, optional): A list of recipient addresses. Recipients are others whom the author wishes to publicly inform of the message (carbon copy)
            reply_to (list, optional): A list of recipient addresses used in the “Reply-To” header when sending the email.
            subject (str, optional): The subject line of the email.
            context_vars (dict, optional): An object containing key and values ​​that will be used by the template.
            files (list, optional): A list containing the files that will be sent together to the email. E.g: [{"name": "file.pdf", "content": "PCFkb2N0eXBlIGh0bWw+..."}]
        """

        data = {
            "subject": subject,
            "to_email": to_email,
            "bcc": bcc,
            "cc": cc,
            "reply_to": reply_to,
            "from_connection": from_connection,
            "template_name": template_name,
            "context_vars": context_vars,
        }

        if files:
            data["base64_files"] = []

            for file in files:
                data["base64_files"].append(
                    {
                        "name": file["name"],
                        "content": self.__get_file(file=file["file"]),
                    }
                )

        return self.http.post(
            url=f"{self.severino_api_url}{self.path}/send/", data=data
        )

    def __get_file(self, file):
        if isinstance(file, str):
            file = open(file, "rb")
            file = file.read()

        return base64.b64encode(file).decode("utf8")


class MailCarrierTemplate:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/mail-carrier/mail-template"

    def test_template(self, template_path: str, context_vars: dict):
        html = ""

        with open(template_path, "rb") as file:
            html = file.read()

        template = Environment(loader=BaseLoader()).from_string(html.decode("utf-8"))

        temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        temp_file.write(str(template.render(**context_vars)).encode("utf-8"))
        temp_file.flush()
        temp_file.close()

        webbrowser.open_new_tab(temp_file.name)
        os.remove(temp_file.name)

    def update(self, template_name: str, template_path: str):
        template_data = None

        check_if_exists = self.http.get(
            url=f"{self.severino_api_url}{self.path}/", params={"name": template_name}
        ).json()

        if not check_if_exists["count"] > 0:
            template_data = self.http.post(
                url=f"{self.severino_api_url}{self.path}/",
                data={
                    "name": template_name,
                    "base64_html": self.__get_file(template_path),
                },
            ).json()

        if not template_data:
            template_data = self.http.put(
                url=f"{self.severino_api_url}{self.path}/{check_if_exists['results'][0]['id']}/",
                data={
                    "name": template_name,
                    "base64_html": self.__get_file(template_path),
                },
            ).json()

        print("\x1b[6;30;42m" + " Template created/updated successfully " + "\x1b[0m")

    def delete(self, template_name):
        check_if_exists = self.http.get(
            url=f"{self.severino_api_url}{self.path}/", params={"name": template_name}
        ).json()

        if not check_if_exists["count"] > 0:
            print("\033[31m" + " Template not found ")
            return

        self.http.delete(
            url=f"{self.severino_api_url}{self.path}/{check_if_exists['results'][0]['id']}/"
        )

        print("\x1b[6;30;42m" + " Template deleted successfully " + "\x1b[0m")

    def __get_file(self, file_path):
        file = open(file_path, "rb")
        file = file.read()
        return base64.b64encode(file).decode("utf8")
