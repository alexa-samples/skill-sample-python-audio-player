# -*- coding: utf-8 -*-

import logging
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream)

from alexa import data, util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ######################### INTENT HANDLERS #########################
# This section contains handlers for the built-in intents and generic
# request handlers like launch, session end, skill events etc.


class CheckAudioInterfaceHandler(AbstractRequestHandler):
    """Check if device supports audio play.

    This can be used as the first handler to be checked, before invoking
    other handlers, thus making the skill respond to unsupported devices
    without doing much processing.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        if handler_input.request_envelope.context.system.device:
            # Since skill events won't have device information
            return handler_input.request_envelope.context.system.device.supported_interfaces.audio_player is None
        else:
            return False

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CheckAudioInterfaceHandler")
        handler_input.response_builder.speak(
            data.DEVICE_NOT_SUPPORTED).set_should_end_session(True)
        return handler_input.response_builder.response


class LaunchRequestHandler(AbstractRequestHandler):
    """Launch radio for skill launch or PlayAudio intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")

        playback_info = util.get_playback_info(handler_input)

        if not playback_info.get('has_previous_playback_session'):
            message = data.WELCOME_MSG
            reprompt = data.WELCOME_REPROMPT_MSG
        else:
            playback_info['in_playback_session'] = False
            message = data.WELCOME_PLAYBACK_MSG.format(
                data.AUDIO_DATA[
                    playback_info.get("play_order")[
                        playback_info.get("index")]].get("title"))
            reprompt = data.WELCOME_PLAYBACK_REPROMPT_MSG

        return handler_input.response_builder.speak(message).ask(
            reprompt).response


class StartPlaybackHandler(AbstractRequestHandler):
    """Handler for Playing audio on different events.

    Handles PlayAudio Intent, Resume Intent.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.ResumeIntent")(handler_input)
                or is_intent_name("PlayAudio")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In StartPlaybackHandler")
        return util.Controller.play(handler_input)


class NextPlaybackHandler(AbstractRequestHandler):
    """Handler for Playing next audio on different events.

    Handles Next Intent and NextCommandIssued event.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.NextIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NextPlaybackHandler")
        return util.Controller.play_next(handler_input)


class PreviousPlaybackHandler(AbstractRequestHandler):
    """Handler for Playing previous audio on different events.

    Handles Previous Intent and PreviousCommandIssued event.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.PreviousIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PreviousPlaybackHandler")
        return util.Controller.play_previous(handler_input)


class PausePlaybackHandler(AbstractRequestHandler):
    """Handler for stopping audio.

    Handles Stop, Cancel and Pause Intents and PauseCommandIssued event.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and (is_intent_name("AMAZON.StopIntent")(handler_input)
                     or is_intent_name("AMAZON.CancelIntent")(handler_input)
                     or is_intent_name("AMAZON.PauseIntent")(handler_input)))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("PausePlaybackHandler")
        return util.Controller.stop(handler_input)


class LoopOnHandler(AbstractRequestHandler):
    """Handler for setting the audio loop on."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.LoopOnIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LoopOnHandler")
        persistent_attr = handler_input.attributes_manager.persistent_attributes
        playback_setting = persistent_attr.get("playback_setting")
        playback_setting["loop"] = True

        return handler_input.response_builder.speak(data.LOOP_ON_MSG).response


class LoopOffHandler(AbstractRequestHandler):
    """Handler for setting the audio loop off."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.LoopOffIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LoopOffHandler")
        persistent_attr = handler_input.attributes_manager.persistent_attributes
        playback_setting = persistent_attr.get("playback_setting")
        playback_setting["loop"] = False

        return handler_input.response_builder.speak(
            data.LOOP_OFF_MSG).response


class ShuffleOnHandler(AbstractRequestHandler):
    """Handler for setting the audio shuffle on."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.ShuffleOnIntent")(
                    handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ShuffleOnHandler")
        persistent_attr = handler_input.attributes_manager.persistent_attributes
        playback_setting = persistent_attr.get("playback_setting")
        playback_info = persistent_attr.get("playback_info")

        playback_setting["shuffle"] = True
        playback_info["play_order"] = util.shuffle_order()
        playback_info["index"] = 0
        playback_info["offset_in_ms"] = 0
        playback_info["playback_index_changed"] = True
        return util.Controller.play(handler_input)


class ShuffleOffHandler(AbstractRequestHandler):
    """Handler for setting the audio shuffle off."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.ShuffleOffIntent")(
                    handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ShuffleOffHandler")
        persistent_attr = handler_input.attributes_manager.persistent_attributes
        playback_setting = persistent_attr.get("playback_setting")
        playback_info = persistent_attr.get("playback_info")

        playback_setting["shuffle"] = False
        playback_info["index"] = playback_info["play_order"][
            playback_info["index"]]
        playback_info["play_order"] = [l for l in range(
            0, len(data.AUDIO_DATA))]
        return util.Controller.play(handler_input)


class StartOverHandler(AbstractRequestHandler):
    """Handler for start over."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.StartOverIntent")(
                    handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In StartOverHandler")
        playback_info = util.get_playback_info(handler_input)
        playback_info["offset_in_ms"] = 0

        return util.Controller.play(handler_input)


class YesHandler(AbstractRequestHandler):
    """Handler for Yes intent when audio is not playing."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (not playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.YesIntent")(
                    handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In YesHandler")
        return util.Controller.play(handler_input)


class NoHandler(AbstractRequestHandler):
    """Handler for No intent when audio is not playing."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (not playback_info.get("in_playback_session")
                and is_intent_name("AMAZON.NoIntent")(
                    handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NoHandler")
        playback_info = util.get_playback_info(handler_input)

        playback_info["index"] = 0
        playback_info["offset_in_ms"] = 0
        playback_info["playback_index_changed"] = True
        playback_info["has_previous_playback_session"] = False

        return util.Controller.play(handler_input)


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for cancel, stop intents when not playing an audio."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (not playback_info.get("in_playback_session")
                and (is_intent_name("AMAZON.CancelIntent")(handler_input)
                     or is_intent_name("AMAZON.StopIntent")(handler_input)))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")
        return handler_input.response_builder.speak(data.STOP_MSG).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for session end."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        logger.info("Session ended with reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for providing help information to user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        playback_info = util.get_playback_info(handler_input)

        if not playback_info.get('has_previous_playback_session'):
            message = data.HELP_MSG
        elif not playback_info.get('in_playback_session'):
            message = data.HELP_PLAYBACK_MSG
        else:
            message = data.HELP_DURING_PLAY_MSG

        return handler_input.response_builder.speak(message).ask(
            message).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent, for unmatched utterances.

    2018-July-12: AMAZON.FallbackIntent is currently available in all
    English locales. This handler will not be triggered except in that
    locale, so it can be safely deployed for any locale. More info
    on the fallback intent can be found here:
    https://developer.amazon.com/docs/custom-skills/standard-built-in-intents.html#fallback
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(
            data.EXCEPTION_MSG).ask(data.EXCEPTION_MSG)
        return handler_input.response_builder.response


# ########## AUDIOPLAYER INTERFACE HANDLERS #########################
# This section contains handlers related to Audioplayer interface

class PlaybackStartedEventHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStarted Directive received.

    Confirming that the requested audio file began playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackStartedHandler")

        playback_info = util.get_playback_info(handler_input)

        playback_info["token"] = util.get_token(handler_input)
        playback_info["index"] = util.get_index(handler_input)
        playback_info["in_playback_session"] = True
        playback_info["has_previous_playback_session"] = True

        return handler_input.response_builder.response

class PlaybackFinishedEventHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFinished Directive received.

    Confirming that the requested audio file completed playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackFinishedHandler")

        playback_info = util.get_playback_info(handler_input)

        playback_info["in_playback_session"] = False
        playback_info["has_previous_playback_session"] = False
        playback_info["next_stream_enqueued"] = False

        return handler_input.response_builder.response


class PlaybackStoppedEventHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStopped Directive received.

    Confirming that the requested audio file stopped playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackStoppedHandler")

        playback_info = util.get_playback_info(handler_input)

        playback_info["token"] = util.get_token(handler_input)
        playback_info["index"] = util.get_index(handler_input)
        playback_info["offset_in_ms"] = util.get_offset_in_ms(
            handler_input)

        return handler_input.response_builder.response


class PlaybackNearlyFinishedEventHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackNearlyFinished Directive received.

    Replacing queue with the URL again. This should not happen on live streams.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackNearlyFinishedHandler")

        persistent_attr = handler_input.attributes_manager.persistent_attributes
        playback_info = persistent_attr.get("playback_info")
        playback_setting = persistent_attr.get("playback_setting")

        if playback_info.get("next_stream_enqueued"):
            return handler_input.response_builder.response

        enqueue_index = (playback_info.get("index") + 1) % len(data.AUDIO_DATA)
        if enqueue_index == 0 and not playback_setting.get("loop"):
            return handler_input.response_builder.response

        playback_info["next_stream_enqueued"] = True
        enqueue_token = playback_info.get("play_order")[enqueue_index]
        play_behavior = PlayBehavior.ENQUEUE
        podcast = data.AUDIO_DATA[enqueue_token]
        expected_previous_token = playback_info.get("token")
        offset_in_ms = 0

        handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=play_behavior,
                audio_item=AudioItem(
                    stream=Stream(
                        token=enqueue_token,
                        url=podcast.get("url"),
                        offset_in_milliseconds=offset_in_ms,
                        expected_previous_token=expected_previous_token),
                    metadata=None)))

        return handler_input.response_builder.response


class PlaybackFailedEventHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFailed Directive received.

    Logging the error and restarting playing with no output speech.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackFailedHandler")

        playback_info = util.get_playback_info(handler_input)
        playback_info["in_playback_session"] = False

        logger.info("Playback Failed: {}".format(
            handler_input.request_envelope.request.error))

        return handler_input.response_builder.response


class ExceptionEncounteredHandler(AbstractRequestHandler):
    """Handler to handle exceptions from responses sent by AudioPlayer
    request.
    """
    def can_handle(self, handler_input):
        # type; (HandlerInput) -> bool
        return is_request_type("System.ExceptionEncountered")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExceptionEncounteredHandler")
        logger.info("System exception encountered: {}".format(
            handler_input.request_envelope.request))
        return handler_input.response_builder.response

# ###################################################################

# ########## PLAYBACK CONTROLLER INTERFACE HANDLERS #################
# This section contains handlers related to Playback Controller interface
# https://developer.amazon.com/docs/custom-skills/playback-controller-interface-reference.html#requests

class PlayCommandHandler(AbstractRequestHandler):
    """Handler for Play command from hardware buttons or touch control.

    This handler handles the play command sent through hardware buttons such
    as remote control or the play control from Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type(
            "PlaybackController.PlayCommandIssued")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlayCommandHandler")
        return util.Controller.play(handler_input, is_playback=True)


class NextCommandHandler(AbstractRequestHandler):
    """Handler for Next command from hardware buttons or touch
    control.

    This handler handles the next command sent through hardware
    buttons such as remote control or the next control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_request_type(
                    "PlaybackController.NextCommandIssued")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NextCommandHandler")
        return util.Controller.play_next(handler_input, is_playback=True)


class PreviousCommandHandler(AbstractRequestHandler):
    """Handler for Previous command from hardware buttons or touch
    control.

    This handler handles the previous command sent through hardware
    buttons such as remote control or the previous control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)

        return (playback_info.get("in_playback_session")
                and is_request_type(
                    "PlaybackController.PreviousCommandIssued")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PreviousCommandHandler")
        return util.Controller.play_previous(handler_input, is_playback=True)


class PauseCommandHandler(AbstractRequestHandler):
    """Handler for Pause command from hardware buttons or touch control.

    This handler handles the pause command sent through hardware
    buttons such as remote control or the pause control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        playback_info = util.get_playback_info(handler_input)
        return (playback_info.get("in_playback_session")
                and is_request_type(
                    "PlaybackController.PauseCommandIssued")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PauseCommandHandler")
        return util.Controller.stop(handler_input)

# ###################################################################

# ################## EXCEPTION HANDLERS #############################
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)
        handler_input.response_builder.speak(data.EXCEPTION_MSG).ask(
            data.EXCEPTION_MSG)

        return handler_input.response_builder.response

# ###################################################################

# ############# REQUEST / RESPONSE INTERCEPTORS #####################
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class LoadPersistenceAttributesRequestInterceptor(AbstractRequestInterceptor):
    """Check if user is invoking skill for first time and initialize preset."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        persistence_attr = handler_input.attributes_manager.persistent_attributes

        if len(persistence_attr) == 0:
            # First time skill user
            persistence_attr["playback_setting"] = {
                "loop": False,
                "shuffle": False
            }

            persistence_attr["playback_info"] = {
                "play_order": [l for l in range(0, len(data.AUDIO_DATA))],
                "index": 0,
                "offset_in_ms": 0,
                "playback_index_changed": False,
                "token": None,
                "next_stream_enqueued": False,
                "in_playback_session": False,
                "has_previous_playback_session": False
            }
        else:
            # Convert decimals to integers, because of AWS SDK DynamoDB issue
            # https://github.com/boto/boto3/issues/369
            playback_info = persistence_attr.get("playback_info")
            playback_info["index"] = int(playback_info.get("index"))
            playback_info["offset_in_ms"] = int(playback_info.get(
                "offset_in_ms"))
            playback_info["play_order"] = [
                int(l) for l in playback_info.get("play_order")]


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


class SavePersistenceAttributesResponseInterceptor(AbstractResponseInterceptor):
    """Save persistence attributes before sending response to user."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        handler_input.attributes_manager.save_persistent_attributes()
# ###################################################################


sb = StandardSkillBuilder(
    table_name=data.DYNAMODB_TABLE_NAME, auto_create_table=True)

# ############# REGISTER HANDLERS #####################
# Request Handlers
sb.add_request_handler(CheckAudioInterfaceHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExceptionEncounteredHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(YesHandler())
sb.add_request_handler(NoHandler())
sb.add_request_handler(StartPlaybackHandler())
sb.add_request_handler(PlayCommandHandler())
sb.add_request_handler(NextPlaybackHandler())
sb.add_request_handler(NextCommandHandler())
sb.add_request_handler(PreviousPlaybackHandler())
sb.add_request_handler(PreviousCommandHandler())
sb.add_request_handler(PausePlaybackHandler())
sb.add_request_handler(PauseCommandHandler())
sb.add_request_handler(LoopOnHandler())
sb.add_request_handler(LoopOffHandler())
sb.add_request_handler(ShuffleOnHandler())
sb.add_request_handler(ShuffleOffHandler())
sb.add_request_handler(StartOverHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(PlaybackStartedEventHandler())
sb.add_request_handler(PlaybackFinishedEventHandler())
sb.add_request_handler(PlaybackStoppedEventHandler())
sb.add_request_handler(PlaybackNearlyFinishedEventHandler())
sb.add_request_handler(PlaybackStartedEventHandler())
sb.add_request_handler(PlaybackFailedEventHandler())

# Exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Interceptors
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_request_interceptor(LoadPersistenceAttributesRequestInterceptor())

sb.add_global_response_interceptor(ResponseLogger())
sb.add_global_response_interceptor(SavePersistenceAttributesResponseInterceptor())

# AWS Lambda handler
lambda_handler = sb.lambda_handler()
