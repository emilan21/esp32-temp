# HTTP First Milestone

This exercise comes after `docs/wifi-first-milestone.md`.

The goal is simple: send one HTTP request from your ESP32 and log enough information to prove it worked.

Do not combine this with the DHT11 yet. Use dummy data first.

## What you are trying to prove

By the end of this exercise, you want to know these things:

- your ESP32 can make an outbound HTTP request over Wi-Fi
- your code can send a simple payload
- your logs show the request result clearly
- you understand the basic request flow before adding sensor logic

## Why dummy data is the right first step

If you try to add real sensor data immediately, you create two possible failure sources:

- sensor reading logic
- network request logic

Using a fixed payload keeps the test narrow.

If HTTP fails, you know it is not the DHT11 yet.

## What to read first

Before writing code, read one official ESP-IDF HTTP client example and focus on:

- `esp_http_client_config_t`
- setting the URL
- event callbacks if the example uses them
- how POST requests are configured
- how headers and body are set
- how response status is checked

You do not need to understand every option. You only need the minimum path for one request.

## First milestone behavior

Your first HTTP version should do only this:

1. boot
2. connect to Wi-Fi
3. send one HTTP request with dummy data
4. log the response status or failure
5. wait or stop

That is enough for the milestone.

## Pick a very simple request

A good first request is an HTTP POST with a tiny JSON body.

Example payload shape:

```json
{
  "device_id": "test-esp32",
  "temp_c": 22,
  "humidity": 50
}
```

Even though those values are fake, the request path is real.

## Code shape to aim for

Do not copy this blindly. Use it as a mental model.

You will likely want:

- a helper like `send_reading_http()`
- one URL string
- a JSON body string
- content type header set to `application/json`
- a log for status code and errors

The flow usually looks like:

```text
app_main()
  -> connect Wi-Fi
  -> prepare JSON string
  -> configure HTTP client
  -> set method to POST
  -> set headers
  -> set body
  -> perform request
  -> log result
```

## Logs you want to see

Useful checkpoints:

- `wifi connected`
- `sending http request`
- `post body prepared`
- `http status: 200`
- `http request failed: ...`

Keep the logs simple but specific.

## Keep the first version minimal

For this milestone, you do not need:

- retries
- TLS unless your server requires it
- parsing a complex response body
- sensor integration
- a full JSON library if a tiny fixed string is enough

Make the easiest thing that proves the network path works.

## What success looks like

You know the milestone is done when:

- Wi-Fi connects reliably first
- the request is sent from the ESP32
- your server or test endpoint receives it
- logs show a clear HTTP status code
- you can repeat the test without guessing what changed

## Good test targets

For learning, it helps to use a simple endpoint you control or can inspect easily.

Good options:

- your own local server on the same network
- a temporary test endpoint that shows request data
- a small API route that logs the body server-side

Pick something where you can confirm both:

- the ESP32 thinks it sent the request
- the server actually received it

## Common beginner problems

- server URL is wrong
- device can reach Wi-Fi but not the server host
- using HTTPS too early and adding certificate complexity
- forgetting the `Content-Type: application/json` header
- malformed JSON string
- not checking the HTTP status code
- assuming request success because no crash happened

## A simple debugging order

If the request does not work, check in this order:

1. Wi-Fi is really connected
2. server URL is correct
3. server is reachable from the ESP32's network
4. request method and headers are correct
5. JSON body is valid enough for the server
6. status code and error logs tell a consistent story

Keep the problem narrow. Change one thing at a time.

## Nice-to-have next step after HTTP works

Once dummy HTTP requests work, the next milestone should be DHT11 reads printed to logs.

Then you can replace the dummy JSON values with real sensor values.

## Suggested checkpoint note

When this milestone works, write down:

- which endpoint you tested against
- what a successful status code looks like
- the exact payload shape you sent
- whether you used HTTP or HTTPS
- the one command you used most often to test it

That note will make later debugging much easier.
