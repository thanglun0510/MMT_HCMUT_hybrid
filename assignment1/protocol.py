def create_message(sender, message):
    return {
        "type": "chat",
        "from": sender,
        "message": message
    }
