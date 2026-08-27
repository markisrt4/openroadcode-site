---
layout: default
title: ZeroMQ Interfaces
description: Open Road Code PUB/SUB topics, REQ/REP commands, endpoints, ownership, and interface design descriptions.
permalink: /messaging/
---
<link rel="stylesheet" href="{{ '/assets/css/messaging.css' | relative_url }}">

<section class="hardware-hero"><div class="container"><p class="eyebrow">Interface documentation</p><div class="hardware-hero__title"><h1>ZeroMQ messaging interfaces.</h1><p>A single map of Open Road Code inter-process communication: asynchronous PUB/SUB telemetry, acknowledged REQ/REP commands, the services that own them, and the IDDs that define their wire contracts.</p></div></div></section>

<section class="section messaging-doc"><div class="container prose" markdown="1">

## Messaging model

Open Road Code deliberately separates **state dissemination** from **commands**. Telemetry that many independent consumers may observe uses ZeroMQ PUB/SUB. Operations that require an acknowledgement or failure response use ZeroMQ REQ/REP.

<div class="architecture-diagram"><pre>                           Open Road Code IPC
                                  |
                 +----------------+----------------+
                 |                                 |
             PUB / SUB                         REQ / REP
          asynchronous state               acknowledged command
                 |                                 |
       XSUB &lt;-- broker --&gt; XPUB             service-owned endpoint
       :5556              :5557                     |
                 |                                 |
       navigation / vehicle                navigation commands
       guidance / future state             route calculation</pre></div>

### PUB/SUB bus topology

Publishers connect to `tcp://127.0.0.1:5556`. Subscribers connect to `tcp://127.0.0.1:5557`. The ZeroMQ broker binds those ports and proxies XSUB to XPUB. Public messages are multipart frames: a UTF-8 topic followed by a JSON payload. Topic constants and payload codecs live under `messaging/contracts/`.

### REQ/REP topology

Commands do not pass through the telemetry broker. A client connects directly to the service-owned command endpoint, sends one JSON request, and receives exactly one JSON response. The navigation command endpoint defaults to `tcp://127.0.0.1:5560` and may be overridden by runtime configuration.

## PUB/SUB topic catalog

<div class="messaging-table-wrap"><table><thead><tr><th>Topic</th><th>Owner / producer</th><th>Purpose</th><th>IDD</th><th>Status</th></tr></thead><tbody>
<tr><td><code>openroad.navigation.position</code></td><td>Navigation service / NavigationStatePublisher</td><td>Absolute geographic position, altitude, speed, course, GNSS fix and satellite metadata.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/idd/navigation_position_state.md">Navigation Position State</a></td><td>master</td></tr>
<tr><td><code>openroad.navigation.motion</code></td><td>Navigation service / NavigationStatePublisher</td><td>Heading, ground speed, vertical speed, turn rate, and motion cache state.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">Message Bus IDD</a></td><td>master</td></tr>
<tr><td><code>openroad.navigation.attitude</code></td><td>Navigation service / NavigationStatePublisher</td><td>Fused heading, pitch, and roll orientation.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">Message Bus IDD</a></td><td>master</td></tr>
<tr><td><code>openroad.navigation.imu</code></td><td>Navigation service / NavigationStatePublisher</td><td>Acceleration, linear acceleration, and angular velocity XYZ vectors.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">Message Bus IDD</a></td><td>master</td></tr>
<tr><td><code>openroad.vehicle.state</code></td><td>Automotive service / VehicleStatePublisher</td><td>Normalized vehicle telemetry including engine speed, vehicle speed, throttle, pressures, temperatures, fuel level, airflow, and control voltage.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/idd/automotive_vehicle_state.md">Automotive Vehicle State</a></td><td>master</td></tr>
<tr><td><code>route_guidance.state</code></td><td>Navigation session / RouteGuidancePublisher</td><td>Active-route progress, remaining distance, maneuver instructions, off-route state, and route-complete state.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/route_guidance_state.md">Route Guidance State</a></td><td><code>navigation_zmq</code></td></tr>
</tbody></table></div>

### Common telemetry contract rules

Public telemetry is presentation-neutral. Physical quantities use SI units, normalized quantities use `0.0..1.0`, payloads are versioned JSON objects, and unavailable nullable values are represented explicitly as `null`. Consumers should not care whether a producer is backed by physical hardware, simulation, a browser, Android sensors, CAN, OBD-II, or another source.

The common conceptual envelope is:

```json
{
  "version": 1,
  "timestamp": {"seconds": 1787337000, "nanoseconds": 123456000},
  "source": "producer-name",
  "data": {}
}
```

Individual IDDs define the exact fields, units, ranges, nullability, validation rules, and any documented exceptions.

## REQ/REP command catalog

The navigation service owns command semantics. The ZeroMQ command server owns transport only. Applications should normally use the request-handler interface rather than constructing or controlling navigation hardware directly.

<div class="messaging-table-wrap"><table><thead><tr><th>Command</th><th>Arguments</th><th>Response</th><th>IDD</th><th>Status</th></tr></thead><tbody>
<tr><td><code>navigation.calibrate_stationary</code></td><td><code>sample_count</code> (default 100), <code>sample_interval_s</code> (default 0.01)</td><td>Success/failure acknowledgement. Successful message: stationary calibration complete.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/navigation_command_service.md">Navigation Command Service</a></td><td><code>navigation_zmq</code></td></tr>
<tr><td><code>navigation.reset_heading</code></td><td><code>heading_deg</code> (default 0.0)</td><td>Success/failure acknowledgement. Successful message: heading reset complete.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/navigation_command_service.md">Navigation Command Service</a></td><td><code>navigation_zmq</code></td></tr>
<tr><td><code>navigation.route.calculate</code></td><td>Origin, destination, and travel mode: <code>AUTO</code>, <code>BICYCLE</code>, <code>PEDESTRIAN</code>, or <code>MOTORCYCLE</code>.</td><td>Route distance/duration, shape points, and maneuver list, or a structured failure response.</td><td><a href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/navigation_command_service.md">Navigation Command Service</a></td><td><code>navigation_zmq</code></td></tr>
</tbody></table></div>

### Request envelope

```json
{
  "command": "navigation.route.calculate",
  "arguments": {}
}
```

### Response envelope

```json
{
  "ok": true,
  "message": "Route calculated",
  "data": {}
}
```

Failures use the same response shape with `ok` set to `false`, a human-readable reason in `message`, and command-specific `data` omitted or set to `null`.

## Interface ownership

<div class="messaging-table-wrap"><table><thead><tr><th>Layer</th><th>Responsibility</th></tr></thead><tbody>
<tr><td><code>messaging/contracts/</code></td><td>Public topic names, JSON message representations, codecs, validators, decoders, and publisher helpers.</td></tr>
<tr><td><code>messaging/zeromq/</code></td><td>ZeroMQ transport primitives, endpoints, broker, publisher, and subscriber implementation.</td></tr>
<tr><td><code>services/navigation/</code></td><td>Owns the live navigation controller, publishes navigation state, and executes navigation command semantics.</td></tr>
<tr><td><code>services/automotive/</code></td><td>Owns automotive acquisition/runtime and publishes normalized vehicle state.</td></tr>
<tr><td><code>docs/idd/</code></td><td>Normative domain interface definitions: field meanings, types, units, ranges, nullability, framing, producer rules, and consumer rules.</td></tr>
<tr><td><code>docs/messaging/message_bus_idd.md</code></td><td>Normative bus-level topology, framing, lifecycle, threading, configuration, and extension rules.</td></tr>
</tbody></table></div>

## Why both patterns exist

PUB/SUB is intentionally lossy and decoupled. A dashboard, logger, diagnostics process, and web UI can all subscribe to vehicle speed without the producer knowing any of them exist. A late subscriber simply starts receiving current state.

REQ/REP represents an operation rather than state. Calibration, heading reset, and route calculation need a definite result, validation errors, and timeout behavior. Putting those operations on PUB/SUB would force clients to invent correlation and acknowledgement machinery, thereby slowly recreating REQ/REP with more bugs and considerably more enthusiasm.

## Source documentation

The repository's <a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">Message Bus IDD</a> is the authoritative bus-level contract. The <a href="https://github.com/markisrt4/OpenRoadCode/blob/master/messaging/README.md">messaging README</a> provides implementation and usage examples. Domain-specific IDDs linked above are authoritative for individual payload semantics.

<p class="callout"><strong>Branch note:</strong> This page deliberately shows both interfaces already present on <code>master</code> and the newer route-guidance / command contracts currently on <code>navigation_zmq</code>. The status column makes that boundary explicit rather than pretending unfinished interfaces have magically teleported into master.</p>

</div></section>
