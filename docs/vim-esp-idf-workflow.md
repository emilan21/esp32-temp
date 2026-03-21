# Minimal Vim + ESP-IDF Workflow

This is a practical workflow for learning embedded development without leaving the terminal.

## Daily loop

The basic cycle is:

1. edit code in Vim
2. build with `idf.py build`
3. flash with `idf.py flash`
4. monitor logs with `idf.py monitor`

When iterating quickly, use:

```sh
idf.py flash monitor
```

## Most useful commands

### Project setup

```sh
idf.py set-target esp32
idf.py menuconfig
```

### Build and run

```sh
idf.py build
idf.py flash
idf.py monitor
idf.py flash monitor
```

### Clean rebuild when things get weird

```sh
idf.py fullclean
idf.py build
```

Use `fullclean` sparingly. Most of the time a normal rebuild is enough.

## Suggested terminal layout

If you like a plain CLI setup, a good arrangement is:

- terminal 1: Vim editing session
- terminal 2: `idf.py flash monitor`
- terminal 3: docs, notes, or `git diff`

This works well in `tmux`, but it is optional.

## Helpful Vim habits

You do not need a big plugin setup to be productive.

Focus on these basics first:

- open files quickly with `:e path/to/file`
- jump to line with `:123`
- search with `/pattern`
- split windows with `:split` or `:vsplit`
- use `:make` only if you want to wire build commands into Vim later

For now, it is perfectly fine to run build commands in a separate shell.

## Suggested project workflow

For this repo, use a simple sequence:

### 1. Start the day

```sh
vim main/esp32-temp.c
```

### 2. Make one tiny change

Examples:

- add one log line
- add one helper function
- configure one GPIO
- change one delay value

### 3. Build immediately

```sh
idf.py build
```

Fix warnings and errors while the change is still fresh.

### 4. Flash and monitor

```sh
idf.py flash monitor
```

Look for:

- boot success
- your own log lines
- sensor values
- Wi-Fi events
- HTTP status codes

### 5. Keep notes

Track a few things in a plain text note:

- what you changed
- what command you ran
- what happened
- what you want to try next

That habit is surprisingly useful in embedded work.

## Beginner-friendly coding style

In embedded C, boring code is good code.

Aim for:

- short functions
- obvious names
- one responsibility per function
- explicit error checks
- small, testable steps

Avoid early on:

- deep abstractions
- macro-heavy designs
- large files with mixed responsibilities
- changing many things before testing once

## A good first workflow for your temperature project

Build the project in this order:

1. `app_main()` logs a boot message
2. Wi-Fi connects and logs an IP
3. DHT11 reads and logs temperature
4. HTTP POST sends dummy JSON
5. HTTP POST sends real sensor data

Do not combine steps until each one works by itself.

## Common beginner traps

- assuming the bug is in C when it is really wiring or power
- changing code and hardware at the same time
- reading the entire manual instead of solving the next small step
- debugging without enough log output
- polling the DHT11 too quickly

## If you want a slightly nicer CLI setup later

Useful tools, but not required:

- `tmux` for split panes
- `ripgrep` for fast code search
- `clang-format` for consistent formatting
- `bear` or LSP tooling if you later want completion support in Vim

Start simple. Add tools only when a real pain point shows up.
