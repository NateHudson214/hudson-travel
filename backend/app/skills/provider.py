"""One bounded OpenAI request; transport injection in tests, no automatic retries."""
import asyncio
import hashlib
import json
from pathlib import Path

import httpx

from .replies import approved_context, render_reply
from .sessions import canonical_json

MODEL = 'gpt-6-luna'
TIMEOUT_SECONDS = 3.0
MAX_OUTPUT_TOKENS = 512
MAX_INPUT_BYTES = 20000
INSTRUCTIONS = Path(__file__).with_name('prompts').joinpath('selector-v1.md').read_text()
PROMPT_HASH = hashlib.sha256(INSTRUCTIONS.encode()).hexdigest()


class ProviderFailure(Exception):
    def __init__(self, category):
        self.category = category
        super().__init__(category)


def request_body(context):
    catalog = approved_context()
    schema = {'type': 'object', 'additionalProperties': False,
              'properties': {'reply_id': {'type': 'string', 'enum': list(catalog['replies'])},
                             'fact_ids': {'type': 'array', 'maxItems': 2,
                                          'items': {'type': 'string', 'enum': list(catalog['facts'])}}},
              'required': ['reply_id', 'fact_ids']}
    text = canonical_json(context)
    body = {'model': MODEL, 'store': False, 'service_tier': 'default',
            'max_output_tokens': MAX_OUTPUT_TOKENS, 'instructions': INSTRUCTIONS,
            'input': [{'role': 'user', 'content': text}],
            'text': {'format': {'type': 'json_schema', 'name': 'skills_reply',
                                'strict': True, 'schema': schema}}}
    if len(canonical_json(body).encode()) > MAX_INPUT_BYTES:
        raise ProviderFailure('context_too_large')
    return body


def parse_response(data):
    if type(data) is not dict or data.get('status') != 'completed':
        raise ProviderFailure('response_rejected')
    # Reasoning metadata may accompany one assistant message; no other outputs.
    output = data.get('output')
    if type(output) is not list:
        raise ProviderFailure('response_rejected')
    messages = [x for x in output if type(x) is dict and x.get('type') == 'message']
    if len(messages) != 1 or any(type(x) is not dict or x.get('type') not in {'message', 'reasoning'} for x in output):
        raise ProviderFailure('response_rejected')
    message = messages[0]
    parts = message.get('content')
    if message.get('role') != 'assistant' or message.get('status') != 'completed' or type(parts) is not list or len(parts) != 1:
        raise ProviderFailure('response_rejected')
    part = parts[0]
    if type(part) is not dict or part.get('type') != 'output_text' or type(part.get('text')) is not str or len(part['text']) > 2000:
        raise ProviderFailure('response_rejected')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate key')
            result[key] = value
        return result
    try:
        selection = json.loads(part['text'], object_pairs_hook=unique)
        render_reply(selection)
        return selection
    except (ValueError, TypeError):
        raise ProviderFailure('response_rejected') from None


async def select_reply(context, key, *, transport=None):
    if not key:
        raise ProviderFailure('configuration')
    body = request_body(context)
    async def dispatch():
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, transport=transport,
                                     follow_redirects=False, trust_env=False) as client:
            async with client.stream('POST', 'https://api.openai.com/v1/responses',
                                     headers={'Authorization': 'Bearer ' + key}, json=body) as response:
                if response.status_code != 200:
                    category = {401: 'authentication', 403: 'authentication', 429: 'rate_limit'}.get(response.status_code, 'provider_http')
                    raise ProviderFailure(category)
                chunks, size = [], 0
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > 65536:
                        raise ProviderFailure('response_rejected')
                    chunks.append(chunk)
                try:
                    return parse_response(json.loads(b''.join(chunks)))
                except (ValueError, TypeError):
                    raise ProviderFailure('response_rejected') from None
    try:
        return await asyncio.wait_for(dispatch(), TIMEOUT_SECONDS)
    except (TimeoutError, httpx.TimeoutException):
        raise ProviderFailure('timeout') from None
    except httpx.HTTPError:
        raise ProviderFailure('transport') from None
