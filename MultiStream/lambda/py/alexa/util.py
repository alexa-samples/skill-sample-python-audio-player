# -*- coding: utf-8 -*-

import random
from typing import List, Dict
from ask_sdk_model import IntentRequest, Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, StopDirective)
from ask_sdk_core.handler_input import HandlerInput
from . import data


def get_playback_info(handler_input):
    # type: (HandlerInput) -> Dict
    persistence_attr = handler_input.attributes_manager.persistent_attributes
    return persistence_attr.get('playback_info')


def can_throw_card(handler_input):
    # type: (HandlerInput) -> bool
    playback_info = get_playback_info(handler_input)
    if (isinstance(handler_input.request_envelope.request, IntentRequest)
            and playback_info.get('playback_index_changed')):
        playback_info['playback_index_changed'] = False
        return True
    else:
        return False


def get_token(handler_input):
    """Extracting token received in the request."""
    # type: (HandlerInput) -> str
    return handler_input.request_envelope.request.token


def get_index(handler_input):
    """Extracting index from the token received in the request."""
    # type: (HandlerInput) -> int
    token = int(get_token(handler_input))
    persistent_attr = handler_input.attributes_manager.persistent_attributes

    return persistent_attr.get("playback_info").get("play_order").index(token)


def get_offset_in_ms(handler_input):
    """Extracting offset in milliseconds received in the request"""
    # type: (HandlerInput) -> int
    return handler_input.request_envelope.request.offset_in_milliseconds


def shuffle_order():
    # type: () -> List
    podcast_indices = [l for l in range(0, len(data.AUDIO_DATA))]
    random.shuffle(podcast_indices)
    return podcast_indices


class Controller:
    """Audioplayer and Playback Controller."""
    @staticmethod
    def play(handler_input, is_playback=False):
        # type: (HandlerInput) -> Response
        playback_info = get_playback_info(handler_input)
        response_builder = handler_input.response_builder

        play_order = playback_info.get("play_order")
        offset_in_ms = playback_info.get("offset_in_ms")
        index = playback_info.get("index")

        play_behavior = PlayBehavior.REPLACE_ALL
        podcast = data.AUDIO_DATA[play_order[index]]
        token = play_order[index]
        playback_info['next_stream_enqueued'] = False

        response_builder.add_directive(
            PlayDirective(
                play_behavior=play_behavior,
                audio_item=AudioItem(
                    stream=Stream(
                        token=token,
                        url=podcast.get("url"),
                        offset_in_milliseconds=offset_in_ms,
                        expected_previous_token=None),
                    metadata=None))
        ).set_should_end_session(True)

        if not is_playback:
            # Add card and response only for events not triggered by
            # Playback Controller
            handler_input.response_builder.speak(
                data.PLAYBACK_PLAY.format(podcast.get("title")))

            if can_throw_card(handler_input):
                response_builder.set_card(SimpleCard(
                    title=data.PLAYBACK_PLAY_CARD.format(
                        podcast.get("title")),
                    content=data.PLAYBACK_PLAY_CARD.format(
                        podcast.get("title"))))

        return response_builder.response

    @staticmethod
    def stop(handler_input):
        # type: (HandlerInput) -> Response
        handler_input.response_builder.add_directive(StopDirective())
        return handler_input.response_builder.response

    @staticmethod
    def play_next(handler_input, is_playback=False):
        # type: (HandlerInput) -> Response
        persistent_attr = handler_input.attributes_manager.persistent_attributes

        playback_info = persistent_attr.get("playback_info")
        playback_setting = persistent_attr.get("playback_setting")
        next_index = (playback_info.get("index") + 1) % len(data.AUDIO_DATA)

        if next_index == 0 and not playback_setting.get("loop"):
            if not is_playback:
                handler_input.response_builder.speak(data.PLAYBACK_NEXT_END)

            return handler_input.response_builder.add_directive(
                StopDirective()).response

        playback_info["index"] = next_index
        playback_info["offset_in_ms"] = 0
        playback_info["playback_index_changed"] = True

        return Controller.play(handler_input, is_playback)

    @staticmethod
    def play_previous(handler_input, is_playback=False):
        # type: (HandlerInput) -> Response
        persistent_attr = handler_input.attributes_manager.persistent_attributes

        playback_info = persistent_attr.get("playback_info")
        playback_setting = persistent_attr.get("playback_setting")
        prev_index = playback_info.get("index") - 1

        if prev_index == -1:
            if playback_setting.get("loop"):
                prev_index += len(data.AUDIO_DATA)
            else:
                if not is_playback:
                    handler_input.response_builder.speak(
                        data.PLAYBACK_PREVIOUS_END)

                return handler_input.response_builder.add_directive(
                    StopDirective()).response

        playback_info["index"] = prev_index
        playback_info["offset_in_ms"] = 0
        playback_info["playback_index_changed"] = True

        return Controller.play(handler_input, is_playback)
