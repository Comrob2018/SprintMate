The proposed additions were derived from a combination of:

1. Existing MITRE EMB3D￼ architecture and stated framework goals
2. MITRE ATT&CK for ICS￼ operational technology tactics and techniques
3. OWASP IoT Security Testing Guide￼ and OWASP Internet of Things Project￼ guidance
4. Industry OT/IoT threat modeling practices
5. Publicly documented MQTT/IoT security research
6. Modern embedded system architectural trends

Below is the traceability matrix you can include directly in the submission package.

⸻

Source and Reference Traceability Matrix

Proposed Area	Supporting Source	Relevance
EMB3D extensibility and evolving framework	MITRE EMB3D Background￼	EMB3D explicitly states it is a living framework intended for additions and revisions
Embedded system threat modeling scope	MITRE EMB3D Main Site￼	Establishes EMB3D as a threat model for embedded systems across critical infrastructure, IoT, manufacturing, healthcare, automotive, etc.
EMB3D future expansion philosophy	MITRE EMB3D Release Statement￼	MITRE states EMB3D is intended to evolve with new threats and mitigations
ATT&CK interoperability	MITRE EMB3D Announcement￼	EMB3D already aligns with ATT&CK, CWE, and CVE
ICS operational relevance	MITRE ATT&CK ICS Matrix￼	Demonstrates ICS-focused tactics and techniques already used in OT environments
Industrial process impacts	MITRE ICS Techniques￼	ICS techniques include physical process manipulation and industrial control impacts
OT/ICS convergence rationale	Nozomi ATT&CK for ICS Guide￼	Describes operational technology focus on PLCs, actuators, sensors, and safety systems
IIoT and smart manufacturing threats	ISA ATT&CK for ICS Strategies￼	Discusses IIoT-specific attack vectors and remote-service exploitation
IoT ecosystem security concerns	OWASP Internet of Things Project￼	Establishes common IoT security weaknesses
IoT testing methodology	OWASP IoT Security Testing Guide￼	Provides IoT-focused testing methodology covering wireless, firmware, APIs, and cloud services
Expandable IoT security methodology	OWASP ISTG Introduction￼	Supports modular expansion and technology-specific testing additions
MQTT attack surface rationale	OWASP MQTT Guide￼	Establishes MQTT manipulation and IoT communication risks
MQTT implementation security risks	MQTT Security Assessment Research￼	Demonstrates exploitable weaknesses in MQTT implementations
MQTT attack detection research	MQTT IoT IDS Research￼	Demonstrates real-world MQTT-based attack modeling
MQTT operational security concerns	MQTT Security Best Practices￼	Discusses authentication, authorization, encryption, and telemetry protection
Industrial MQTT exposure	Securing MQTT for IIoT￼	Discusses MQTT risks in industrial IoT environments
IoT update mechanism risks	OWASP IoT Vulnerabilities Overview￼	Supports OTA/update-chain threat proposals
Embedded and OT threat-model evolution	MITRE EMB3D 2.0 Coverage Expansion￼	Shows EMB3D threat coverage is already expanding
ATT&CK framework adaptability	MITRE ATT&CK State of the Art Research￼	Supports ATT&CK extensibility into new operational domains
ATT&CK interoperability with ML/AI	MITRE ATT&CK Applications Research￼	Discusses ATT&CK integration with ML and evolving cybersecurity domains
IoT lifecycle security	ENISA IoT Security Recommendations￼	Supports SBOM, lifecycle, dependency, and update-chain concerns

⸻

Source Justification for Each Proposed Threat Family

⸻

Wireless Threat Extensions

Supporting Sources

* OWASP IoT Security Testing Guide￼
* OWASP Internet of Things Project￼
* Nozomi ATT&CK for ICS Guide￼

Derived Rationale

These sources discuss:

* wireless exposure
* proximity attacks
* insecure communications
* IoT protocol testing
* device-level attack surfaces

These directly support proposed additions such as:

* RF replay
* rogue pairing
* BLE spoofing
* wireless denial of service

⸻

Industrial / OT Threat Extensions

Supporting Sources

* MITRE ICS Matrix￼
* MITRE ICS Techniques￼
* ISA ATT&CK for ICS Strategies￼
* Nozomi ATT&CK for ICS Guide￼

Derived Rationale

These sources discuss:

* PLC manipulation
* process control impacts
* OT protocol abuse
* operational safety implications
* industrial process attacks

These directly support:

* CAN injection
* Modbus abuse
* OPC UA trust failures
* safety controller manipulation

⸻

Cloud / IoT Threat Extensions

Supporting Sources

* OWASP MQTT Guide￼
* MQTT Security Assessment Research￼
* MQTT IoT IDS Research￼
* Securing MQTT for IIoT￼

Derived Rationale

These sources discuss:

* MQTT abuse
* telemetry compromise
* IoT communication security
* denial of service
* broker weaknesses
* authentication weaknesses

These support:

* MQTT topic hijacking
* telemetry exfiltration
* cloud credential theft
* API exhaustion

⸻

Sensor and Cyber-Physical Threat Extensions

Supporting Sources

* MITRE ICS Techniques￼
* Nozomi ATT&CK for ICS Guide￼
* ISA ATT&CK for ICS Strategies￼

Derived Rationale

These sources discuss:

* sensors
* actuators
* process manipulation
* operational safety
* physical consequences

These support:

* sensor spoofing
* telemetry injection
* actuator command abuse
* GPS spoofing

⸻

Supply Chain Threat Extensions

Supporting Sources

* ENISA IoT Security Recommendations￼
* OWASP IoT Security Testing Guide￼
* MITRE EMB3D Release Statement￼

Derived Rationale

These sources discuss:

* secure update mechanisms
* dependency security
* lifecycle security
* software integrity
* build trust

These support:

* dependency injection
* build pipeline compromise
* unsigned containers
* SBOM mismatch

⸻

AI / ML Embedded Threat Extensions

Supporting Sources

* MITRE ATT&CK Applications Research￼
* MITRE ATT&CK State of the Art Research￼

Derived Rationale

These sources discuss:

* ATT&CK evolution
* ML integration
* emerging cybersecurity domains
* adaptive framework applicability

These support:

* model poisoning
* adversarial input manipulation
* inference leakage
* autonomous decision abuse

⸻

Important Clarification for Submission

A large portion of the proposed threat additions are:

* synthesized framework extensions
* threat-model engineering recommendations
* derived operational mappings

—not direct copies of MITRE content.

That distinction is important because it shows:

* original contribution
* analytical synthesis
* operational modeling
* framework evolution work

rather than merely reproducing existing ATT&CK or EMB3D content.