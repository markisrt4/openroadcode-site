---
layout: default
title: ZeroMQ Interfaces
description: Open Road Code PUB/SUB topics, REQ/REP commands, endpoints, ownership, and interface design descriptions.
permalink: /messaging/
---
<link rel="stylesheet" href="{{ '/assets/css/messaging.css' | relative_url }}">

<section class="hardware-hero messaging-hero"><div class="container"><p class="eyebrow">Interface documentation</p><div class="hardware-hero__title"><h1>ZeroMQ messaging interfaces.</h1><p>What Open Road Code publishes, what it commands, where each message goes, and the IDD that defines the contract.</p></div></div></section>

<section class="section messaging-doc"><div class="container">
  <div class="messaging-intro">
    <div><p class="section-label">At a glance</p><h2>Two patterns. One IPC layer.</h2><p>Live state uses PUB/SUB so many consumers can listen independently. Operations that need a definite answer use REQ/REP.</p></div>
    <div class="messaging-flow" aria-label="ZeroMQ messaging flow">
      <div class="flow-node flow-node--source">Services</div><div class="flow-arrow">↓</div>
      <div class="flow-split"><div><strong>PUB/SUB</strong><small>live state</small></div><div><strong>REQ/REP</strong><small>commands</small></div></div>
      <div class="flow-split flow-split--bottom"><div><small>broker</small><strong>:5556 → :5557</strong></div><div><small>navigation</small><strong>:5560</strong></div></div>
    </div>
  </div>

  <div class="endpoint-grid">
    <article class="endpoint-card"><span class="endpoint-icon">PUB</span><div><small>Publishers connect</small><code>tcp://127.0.0.1:5556</code><p>Navigation, vehicle, guidance, and future telemetry producers.</p></div></article>
    <article class="endpoint-card"><span class="endpoint-icon endpoint-icon--blue">SUB</span><div><small>Subscribers connect</small><code>tcp://127.0.0.1:5557</code><p>UIs, loggers, diagnostics, and any other state consumer.</p></div></article>
    <article class="endpoint-card"><span class="endpoint-icon endpoint-icon--orange">REQ</span><div><small>Navigation commands</small><code>tcp://127.0.0.1:5560</code><p>Direct service endpoint for acknowledged operations.</p></div></article>
  </div>

  <section class="message-section" id="pubsub">
    <div class="message-section__heading"><div><p class="section-label">PUB / SUB</p><h2>Telemetry topics</h2><p>Multipart messages contain a UTF-8 topic followed by a versioned JSON payload.</p></div><div class="message-thumb message-thumb--gps" aria-hidden="true"></div></div>
    <div class="interface-grid">
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill">POSITION</span><span class="status-pill">master</span></div><h3><code>openroad.navigation.position</code></h3><p>Absolute position, altitude, speed, course, GNSS fix, and satellite metadata.</p><dl><div><dt>Producer</dt><dd>Navigation service</dd></div><div><dt>Publisher</dt><dd><code>NavigationStatePublisher</code></dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/idd/navigation_position_state.md">View Position State IDD →</a></article>
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill">MOTION</span><span class="status-pill">master</span></div><h3><code>openroad.navigation.motion</code></h3><p>Heading, ground speed, vertical speed, turn rate, and motion-cache state.</p><dl><div><dt>Producer</dt><dd>Navigation service</dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">View Message Bus IDD →</a></article>
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill">ATTITUDE</span><span class="status-pill">master</span></div><h3><code>openroad.navigation.attitude</code></h3><p>Fused heading, pitch, and roll orientation.</p><dl><div><dt>Producer</dt><dd>Navigation service</dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">View Message Bus IDD →</a></article>
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill">IMU</span><span class="status-pill">master</span></div><h3><code>openroad.navigation.imu</code></h3><p>Acceleration, linear acceleration, and angular-velocity XYZ vectors.</p><dl><div><dt>Producer</dt><dd>Navigation service</dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">View Message Bus IDD →</a></article>
      <article class="interface-card interface-card--vehicle"><div class="interface-card__top"><span class="type-pill type-pill--blue">VEHICLE</span><span class="status-pill">master</span></div><h3><code>openroad.vehicle.state</code></h3><p>Normalized engine, speed, throttle, pressure, temperature, fuel, airflow, and voltage telemetry.</p><dl><div><dt>Producer</dt><dd>Automotive service</dd></div><div><dt>Publisher</dt><dd><code>VehicleStatePublisher</code></dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/idd/automotive_vehicle_state.md">View Vehicle State IDD →</a></article>
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill type-pill--orange">GUIDANCE</span><span class="status-pill status-pill--branch">navigation_zmq</span></div><h3><code>route_guidance.state</code></h3><p>Route progress, remaining distance, maneuvers, off-route state, and completion.</p><dl><div><dt>Producer</dt><dd>Navigation session</dd></div><div><dt>Publisher</dt><dd><code>RouteGuidancePublisher</code></dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/route_guidance_state.md">View Route Guidance IDD →</a></article>
    </div>

    <details class="doc-details"><summary>Telemetry envelope and contract rules</summary><div class="details-body"><p>Physical quantities use SI units, normalized quantities use <code>0.0..1.0</code>, unavailable nullable values are explicit <code>null</code>, and consumers remain independent of the physical or simulated producer.</p><pre><code>{
  "version": 1,
  "timestamp": {"seconds": 1787337000, "nanoseconds": 123456000},
  "source": "producer-name",
  "data": {}
}</code></pre></div></details>
  </section>

  <section class="message-section" id="reqrep">
    <div class="message-section__heading"><div><p class="section-label">REQ / REP</p><h2>Navigation commands</h2><p>Commands bypass the telemetry broker and go directly to the service that owns the operation.</p></div><div class="message-thumb message-thumb--pi" aria-hidden="true"></div></div>
    <div class="interface-grid interface-grid--commands">
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill type-pill--orange">COMMAND</span><span class="status-pill status-pill--branch">navigation_zmq</span></div><h3><code>navigation.calibrate_stationary</code></h3><p>Runs stationary IMU calibration and returns an explicit success or failure.</p><dl><div><dt>Arguments</dt><dd><code>sample_count</code>, <code>sample_interval_s</code></dd></div><div><dt>Owner</dt><dd>Navigation service</dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/navigation_command_service.md">View Command Service IDD →</a></article>
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill type-pill--orange">COMMAND</span><span class="status-pill status-pill--branch">navigation_zmq</span></div><h3><code>navigation.reset_heading</code></h3><p>Resets the navigation heading reference to a requested heading.</p><dl><div><dt>Arguments</dt><dd><code>heading_deg</code>, default <code>0.0</code></dd></div><div><dt>Owner</dt><dd>Navigation service</dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/navigation_command_service.md">View Command Service IDD →</a></article>
      <article class="interface-card"><div class="interface-card__top"><span class="type-pill type-pill--orange">COMMAND</span><span class="status-pill status-pill--branch">navigation_zmq</span></div><h3><code>navigation.route.calculate</code></h3><p>Calculates a route and returns distance, duration, route shape, and maneuvers.</p><dl><div><dt>Arguments</dt><dd>origin · destination · travel mode</dd></div><div><dt>Modes</dt><dd>AUTO · BICYCLE · PEDESTRIAN · MOTORCYCLE</dd></div></dl><a class="idd-link" href="https://github.com/markisrt4/OpenRoadCode/blob/navigation_zmq/docs/idd/navigation_command_service.md">View Command Service IDD →</a></article>
    </div>

    <details class="doc-details"><summary>Example request and response</summary><div class="details-body"><p><strong>Request</strong></p><pre><code>{
  "command": "navigation.route.calculate",
  "arguments": {}
}</code></pre><p><strong>Response</strong></p><pre><code>{
  "ok": true,
  "message": "Route calculated",
  "data": {}
}</code></pre><p>Failures use the same response shape with <code>ok: false</code> and a human-readable reason.</p></div></details>
  </section>

  <section class="message-section ownership-section"><div class="message-section__heading"><div><p class="section-label">Ownership</p><h2>Where the pieces live</h2></div><div class="message-thumb message-thumb--controls" aria-hidden="true"></div></div>
    <div class="ownership-grid"><div><code>messaging/contracts/</code><p>Topics, codecs, validators, decoders, and publisher helpers.</p></div><div><code>messaging/zeromq/</code><p>Endpoints, broker, publisher, subscriber, and transport primitives.</p></div><div><code>services/navigation/</code><p>Navigation state production and command semantics.</p></div><div><code>services/automotive/</code><p>Vehicle acquisition and normalized vehicle-state publication.</p></div><div><code>docs/idd/</code><p>Normative domain interface definitions.</p></div><div><code>docs/messaging/</code><p>Bus topology, framing, lifecycle, configuration, and extension rules.</p></div></div>
    <details class="doc-details"><summary>Why Open Road Code uses both patterns</summary><div class="details-body"><p><strong>PUB/SUB</strong> is intentionally decoupled: dashboards, loggers, diagnostics, and web UIs can all observe state without the producer knowing they exist.</p><p><strong>REQ/REP</strong> represents operations. Calibration, heading reset, and route calculation need validation, a definite result, and timeout behavior.</p></div></details>
  </section>

  <aside class="messaging-source"><div><p class="section-label">Authoritative contracts</p><h2>Follow the IDD.</h2><p>The website is the readable map. The repository IDDs remain the normative source for field meanings, types, units, ranges, nullability, framing, and producer/consumer rules.</p></div><div class="source-actions"><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/docs/messaging/message_bus_idd.md">Message Bus IDD →</a><a href="https://github.com/markisrt4/OpenRoadCode/blob/master/messaging/README.md">Messaging README →</a></div></aside>
</div></section>