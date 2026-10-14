# Olilo Pulse for Home Assistant

<p align="center">
  <img src="logo.png" alt="Olilo Pulse" width="200">
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant integration for [Olilo Pulse](https://pulse.olilo.co.uk) — continuous network quality monitoring. Track ping latency, packet loss, jitter, and uptime for all your Pulse monitors directly in Home Assistant.

## Features

- **Automatic discovery** of all monitors on your Olilo Pulse account
- **Latency tracking** — average, minimum, and maximum ping latency (ms)
- **Jitter** — network jitter measurement (ms)
- **Packet loss** — percentage of lost packets
- **Uptime** — monitor uptime percentage
- **Status** — binary sensor for monitor up/down connectivity state
- **Per-monitor devices** — each monitor appears as its own device in Home Assistant

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **three dots** menu (top right) → **Custom repositories**
4. Add this repository URL and select **Integration** as the category
5. Click **Add**
6. Search for **Olilo Pulse** and install it
7. Restart Home Assistant

### Manual

1. Copy the `custom_components/olilo_pulse` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Olilo Pulse**
3. Enter your API key (starts with `pulse_`)

## Entities

Each Pulse monitor creates the following entities:

| Entity | Type | Unit | Description |
|---|---|---|---|
| Average latency | Sensor | ms | Average ping latency (24h) |
| Minimum latency | Sensor | ms | Minimum ping latency (24h) |
| Maximum latency | Sensor | ms | Maximum ping latency (24h) |
| Jitter | Sensor | ms | Network jitter (24h) |
| Packet loss | Sensor | % | Packet loss percentage (24h) |
| Uptime | Sensor | % | Monitor uptime percentage (24h) |
| Status | Binary sensor | — | Monitor connectivity (up/down) |

## API

This integration uses the [Olilo Pulse API](https://pulse.olilo.co.uk) (`https://pulse.olilo.co.uk/api/v1`).

- **Authentication**: Bearer token (`pulse_...`)
- **Rate limit**: 100 requests/minute per key
- **Poll interval**: 60 seconds
- **Stats range**: 24 hours

## License

MIT
