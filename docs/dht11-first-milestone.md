# DHT11 First Milestone

This exercise should be done before you combine the sensor with HTTP.

The goal is simple: read the DHT11 successfully and print temperature and humidity to the serial logs.

Do not send readings to the server yet.

## What you are trying to prove

By the end of this exercise, you want to know these things:

- your DHT11 is wired correctly
- your ESP32 can talk to it on the chosen GPIO
- your code can read valid data more than once
- you understand the difference between a valid read and a bad one

## Why the sensor should be isolated first

DHT11 reads depend on timing and wiring.

If you mix this with Wi-Fi and HTTP too early, you can waste time chasing the wrong problem.

A bad reading might come from:

- wrong pin
- missing pull-up resistor
- timing errors
- polling too fast
- power issues

Keep the milestone narrow so the failure is easier to identify.

## What to read first

Before writing code, read:

- the DHT11 pinout for your exact module
- whether the module already includes a pull-up resistor
- the DHT11 message format: humidity, temperature, checksum
- one ESP-IDF-compatible DHT11 reference implementation or example

You are not trying to memorize the protocol timing numbers perfectly. You are trying to understand the handshake and result shape.

## Wiring checklist

Verify these basics before debugging code:

- `VCC` goes to the correct supply for your module
- `GND` goes to ESP32 ground
- `DATA` goes to the GPIO you plan to use
- a pull-up resistor is present if your module does not already have one
- all jumper wires are firmly connected

If wiring is wrong, software changes will not save you.

## First milestone behavior

Your first DHT11 version should do only this:

1. boot
2. initialize the chosen GPIO for sensor use
3. read the DHT11 on a safe interval
4. verify checksum
5. print valid readings or log read failure

That is enough.

## Keep the polling interval reasonable

Do not poll the DHT11 too quickly.

For a beginner test, a slow interval is better, such as:

- 2 seconds
- 5 seconds

That gives you readable logs and avoids stressing a slow sensor.

## Code shape to aim for

Do not copy this blindly. Use it as a mental model.

You will likely want:

- a small data structure for a reading
- a helper like `dht11_read()`
- checksum verification
- logs for success and failure
- a loop with a delay between reads

The flow usually looks like:

```text
app_main()
  -> initialize gpio/timing setup
  -> wait before first read if needed
  -> start DHT11 handshake
  -> measure pulses
  -> decode 40 bits
  -> verify checksum
  -> log temp and humidity
  -> delay and repeat
```

## Logs you want to see

Useful checkpoints:

- `starting dht11 read`
- `sensor response detected`
- `checksum ok`
- `temp_c=23 humidity=51`
- `dht11 read failed`
- `checksum mismatch`

Logs are especially important here because sensor timing bugs are hard to see otherwise.

## Keep the first version minimal

For this milestone, you do not need:

- server uploads
- Wi-Fi integration in the same loop
- averaging across many samples
- fancy error recovery
- perfect architecture

You just need repeatable valid reads.

## What success looks like

You know the milestone is done when:

- the values look plausible for the room
- you get multiple successful reads in a row
- occasional bad reads are understandable and logged clearly
- changing the environment slightly changes the readings

For example, holding the sensor briefly or moving it to a warmer area should affect the temperature reading.

## Common beginner problems

- wrong GPIO selected
- missing pull-up resistor
- using a DHT11 example meant for another platform without understanding timing differences
- polling too fast
- noisy power or shaky jumper wires
- not verifying checksum
- assuming every read must succeed perfectly

## A simple debugging order

If readings are bad, check in this order:

1. wiring and power
2. chosen GPIO
3. pull-up resistor presence
4. polling interval
5. protocol timing logic
6. checksum handling

Do not start by rewriting everything.

## Nice-to-have next step after DHT11 works

Once you can print valid DHT11 readings in the logs, combine that code with the HTTP milestone.

At that point you can replace dummy values with real sensor data.

## Suggested checkpoint note

When this milestone works, write down:

- which GPIO you used
- whether your module needed an external pull-up resistor
- what valid readings looked like in your room
- how often you polled the sensor
- what common failure log messages looked like

That note will help a lot when you integrate the sensor with the rest of the project.
