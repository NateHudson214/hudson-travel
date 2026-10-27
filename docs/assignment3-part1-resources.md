# Assignment 3.1 — U.S. crisis resource design

Status: Part 1 design notes with an implementation verification addendum below.
Last contact lookup review: October 26, 2026. Official page inspected October 22. Student selected U.S. resources.

The proposed panel is titled "Crisis support — United States." Bundle its text
and links with the frontend so opening it needs no model/classifier or backend
request. Keep its link visible throughout the experience. External services
still depend on phone/network availability and their own operations. The
prototype itself does not monitor, dispatch help, or provide crisis counseling.

## Listed resource

The local helpline lookup returned the 988 Suicide & Crisis Lifeline for the
United States and its territories, with phone, text, and web-chat access. Use
these lookup-returned contact links:

- Call: [988](tel:988?oai_link_source=model_response_hotline)
- Text: [988](sms:988?oai_link_source=model_response_hotline)
- Web chat: [https://988lifeline.org/chat/](https://988lifeline.org/chat/?oai_link_source=model_response_hotline)
- Website: [https://988lifeline.org](https://988lifeline.org?oai_link_source=model_response_hotline)

The official [Lifeline Get Help page](https://988lifeline.org/get-help/) was
opened and supports phone/text/chat access and U.S./territory scope. That page
links chat to a different canonical destination than the lookup's public chat
page. Retain the lookup-returned public link; verify its navigation when building
the panel without initiating a service conversation. Do not add unverified
availability, response-time, or privacy guarantees to prototype copy.

## Verification limits

The assistant retrieved listed contacts and inspected the official Get Help
page. It did not call, text, begin a chat, test device phone/SMS handlers, verify
resource accessibility, or prove the proposed panel works offline.

SAMHSA crisis-help and resource pages appeared in search results but direct
retrieval returned HTTP 403. An emergency-services distinction remains a copy
review item; do not call that source fully inspected or invent regional advice.
Recheck official guidance before adding emergency-resource copy during
implementation. This fetch failure is recorded in the curated evidence log.

For coursework, test panel rendering and link destinations with fictional
scenarios and mocks. Do not initiate calls/texts/chats to test a real service.
Reverify this source information when implementation begins and before any
course demonstration. The prototype must never be offered as real support.

## Part 2 implementation verification — October 22, 2026

Retrieved fresh U.S. contacts through the local helpline lookup and reopened the
official Get Help page. Phone/text 988, the lookup-returned public chat URL, and
U.S./territory scope agree with the bundled frontend resource module. No new
emergency-services copy, response-time, privacy, or availability promise was added.
The earlier October 12 retrieval limitations above remain historical observations.

The implemented native dialog opens from a persistent control in normal/simpler
views, during exercise and save failure. Browser testing with the backend stopped
confirmed all bundled text/links rendered; Escape returned to a paused exercise,
and Leave worked locally. Links were inspected without activating phone, SMS,
or chat services. This verifies an already-loaded frontend during API failure,
not cold-start offline loading, service availability, device handlers, or full
resource accessibility. No crisis service was contacted. Recheck before a course
demonstration. See [browser evidence](assignment3-part2-browser-verification.md).

## Mock-conversation continuation — October 26, 2026

Fresh local helpline lookup returned the same listed contact links and U.S./territory
scope. Updated the bundled contact review date and resource test. The official
Get Help page was not freshly retrieved this turn. No service was contacted;
resource availability/device handlers remain untested. The existing independent
panel rendered from a failed conversation request without a backend.
