import json


class Token:
    def __init__(self, data: dict):
        """Constructore method."""
        self.json = data
        self.response = json.dumps(data, indent=4)
        self.token = data["token"]
        self.id = data["id"]


class Message:
    def __init__(self, data: dict):
        self.json = data
        self.response = json.dumps(data, indent=4)
        self.id = data["id"]
        self.accountId = data["accountId"]
        self.msgId = data["msgid"]
        self.From = data["from"]
        self.To = data["to"]
        self.CC = data["cc"]
        self.BCC = data["bcc"]
        self.subject = data["subject"]
        self.seen = data["seen"]
        self.flagged = data["flagged"]
        self.isDeleted = data["isDeleted"]
        self.verifications = data["verifications"]
        self.retention = data["retention"]
        self.retentionDate = data["retentionDate"]
        self.text = data["text"]
        self.html = data["html"]
        self.hasAttachments = data["hasAttachments"]
        self.attachments = data["attachments"]
        self.size = data["size"]
        self.downloadUrl = data["downloadUrl"]
        self.createdAt = data["createdAt"]
        self.updatedAt = data["updatedAt"]


class Account:
    def __init__(self, data: dict):
        self.json = data
        self.response = json.dumps(data, indent=4)
        self.id = data["id"]
        self.address = data["address"]
        self.isDisabled = data["isDisabled"]
        self.isDeleted = data["isDeleted"]
        self.quota = data["quota"]
        self.used = data["used"]
        self.createdAt = data["createdAt"]
        self.updatedAt = data["updatedAt"]


class Domain:
    def __init__(self, data: dict):
        self.json = data
        self.response = json.dumps(data, indent=4)
        self.id = data["id"]
        self.domain = data["domain"]
        self.isActive = data["isActive"]
        self.isPrivate = data["isPrivate"]
        self.createdAt = data["createdAt"]
        self.updatedAt = data["updatedAt"]


class Source:
    id = None
    downloadUrl = None
    data = None
