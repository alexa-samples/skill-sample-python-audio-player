# -*- coding: utf-8 -*-

WELCOME_MSG = "Welcome to the Alexa Dev Chat Podcast. You can say, play the audio to begin the podcast."
WELCOME_REPROMPT_MSG = "You can say, play the audio, to begin."
WELCOME_PLAYBACK_MSG = "You were listening to {}. Would you like to resume?"
WELCOME_PLAYBACK_REPROMPT_MSG = "You can say yes to resume or no to play from the top"
DEVICE_NOT_SUPPORTED = "Sorry, this skill is not supported on this device"
LOOP_ON_MSG = "Loop turned on."
LOOP_OFF_MSG = "Loop turned off."
HELP_MSG = WELCOME_MSG
HELP_PLAYBACK_MSG = WELCOME_PLAYBACK_MSG
HELP_DURING_PLAY_MSG = "You are listening to the Alexa Dev Chat Podcast. You can say, Next or Previous to navigate through the playlist. At any time, you can say Pause to pause the audio and Resume to resume."
STOP_MSG = "Goodbye."
EXCEPTION_MSG = "Sorry, this is not a valid command. Please say help, to hear what you can say."
PLAYBACK_PLAY = "This is {}"
PLAYBACK_PLAY_CARD = "Playing {}"
PLAYBACK_NEXT_END = "You have reached the end of the playlist"
PLAYBACK_PREVIOUS_END = "You have reached the start of the playlist"

DYNAMODB_TABLE_NAME = "Audio-Player-Multi-Stream"

AUDIO_DATA = [
    {
        "title": "Episode 22",
        "url": "https://feeds.soundcloud.com/stream/459953355-user-652822799-episode-022-getting-started-with-alexa-for-business.mp3",
    },
    {
        "title": "Episode 23",
        "url": "https://feeds.soundcloud.com/stream/476469807-user-652822799-episode-023-voicefirst-in-2018-where-are-we-now.mp3",
    },
    {
        "title": "Episode 24",
        "url": "https://feeds.soundcloud.com/stream/496340574-user-652822799-episode-024-the-voice-generation-will-include-all-generations.mp3",
    }
]