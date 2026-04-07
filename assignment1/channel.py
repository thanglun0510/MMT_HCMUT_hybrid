# ========================
# CHANNEL STORAGE
# ========================

channels = {
    "general": []
}

# ========================
# CHANNEL MANAGEMENT
# ========================

def create_channel(name):
    if name not in channels:
        channels[name] = []


def get_channels():
    return list(channels.keys())


# ========================
# MESSAGE MANAGEMENT
# ========================

def add_message(channel, msg):
    if channel not in channels:
        channels[channel] = []

    channels[channel].append(msg)


def get_messages(channel):
    return channels.get(channel, [])


# ========================
# OPTIONAL: ACCESS CONTROL
# ========================

channel_members = {
    # "private": ["peer1"]
}


def can_access(channel, user):
    if channel not in channel_members:
        return True
    return user in channel_members[channel]
