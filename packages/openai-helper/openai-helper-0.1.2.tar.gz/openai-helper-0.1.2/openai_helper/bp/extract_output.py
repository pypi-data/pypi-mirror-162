#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" A Generic Service to Extract Unstructured Output from an OpenAI response """


from pprint import pformat
from baseblock.common_utils import odds_of

from baseblock import Enforcer
from baseblock import BaseObject


class ExtractOutput(BaseObject):
    """ A Generic Service to Extract Unstructured Output from an OpenAI response """

    def __init__(self):
        """
        Created:
            17-Mar-2022
            craig@bast.ai
            *   in pursuit of
                https://github.com/grafflr/graffl-core/issues/222
        Updated:
            18-Mar-2022
            craig@bast.ai
            *   handle text completions
                https://github.com/grafflr/graffl-core/issues/224
        Updated:
            4-Aug-2022
            craig@bast.ai
            *   migrated to 'openai-helper' in pursuit of
                https://bast-ai.atlassian.net/browse/COR-56
        """
        BaseObject.__init__(self, __name__)

    @staticmethod
    def _to_string(results: list) -> str:
        message_text = ' '.join(results)
        while '  ' in message_text:
            message_text = message_text.replace('  ', ' ')
        return message_text.strip()

    def _message_text_extract(self,
                              d_event: dict) -> str or None:
        if 'blocks' in d_event:
            message = []
            elements = d_event['blocks'][0]['elements'][0]['elements']
            if len(elements):
                [message.append(x)
                 for x in [x['text'] for x in elements
                           if x['type'] == 'text']]

            return self._to_string(message)

        elif 'channel' in d_event:
            message_text = d_event['text']
            while '>' in message_text:
                message_text = message_text.split('>')[-1].strip()
            return self._to_string([message_text])

        elif 'choices' in d_event:
            message = []
            for choice in d_event['choices']:
                message.append(choice['text'])
            return self._to_string(message)

        self.logger.error('\n'.join([
            "Event Structure Not Recognized",
            pformat(d_event)]))

        raise NotImplementedError

    def _handle_text_completions(self,
                                 input_text: str) -> str:

        # this represents openAI trying to complete a user sentence
        # openAI will generally do this if the user does not terminate their input with punctuation like .!?
        # graffl now adds ending punctuation where none exists, so this pattern rarely takes place ...
        if input_text.startswith(' ') and '\n\n' in input_text:
            response = input_text.split('\n\n')[-1].strip()
            if response and len(response):
                return response

        # this is more common and seems to represent another form of text completion
        # an example is "0\n\nI'm not sure what you're asking"
        # the text prior to the response tends to be brief
        if '\n\n' in input_text:
            lines = input_text.split('\n\n')
            lines = [x.strip() for x in lines if x]
            lines = [x for x in lines if len(x) > 5]
            input_text = ' '.join(lines)
            while '  ' in input_text:
                input_text = input_text.replace('  ', ' ')

        return input_text

    def process(self,
                d_result: dict) -> str:

        if self.isEnabledForDebug:
            Enforcer.is_dict(d_result)

        # d_result['choices'][0]['text'].strip()
        input_text = self._message_text_extract(d_result)
        summary = self._handle_text_completions(input_text)

        # Sample Input: We are not put in this world for mere pleasure alone.
        # Sample Output: We are not put in this world for mere pleasure alone.  Sometimes, we must suffer through pain and hardship to grow and become stronger.
        # Desired Output: Sometimes, we must suffer through pain and hardship to grow and become stronger.
        if input_text in summary and input_text != summary:
            if odds_of(90):
                summary = summary.replace(input_text, '')

        indicators = ['User:', 'Human:', 'Assistant:']

        for indicator in indicators:
            if indicator in summary:
                summary = summary.split(indicator)[-1].strip()

        if 'User:' in summary:
            summary = summary.replace('User:', '').strip()
        if 'Human:' in summary:
            summary = summary.replace('Human:', '').strip()

        if self.isEnabledForDebug:
            Enforcer.is_str(summary)

        if self.isEnabledForDebug:
            self.logger.debug('\n'.join([
                "ETL Module Completed",
                f"\tInput Text: {input_text}",
                f"\tOutput Text: {summary}"]))

        return summary
