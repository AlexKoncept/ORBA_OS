\# Security Policy / Politique de sécurité



\## Reporting a Vulnerability / Signaler une vulnérabilité



Thank you for helping keep Orba OS safe. To report a security vulnerability, please contact the security maintainer:



\- Email: contact@alexkoncept.com

\- Project author: Alex Koncept

\- Portfolio: https://alexkoncept.github.io/



If you prefer encrypted reports, include a PGP-signed message. Public key (if available) will be listed here.



Please include:

\- Affected component (desktop/backend/mobile/frontend)

\- Steps to reproduce

\- Impact and severity

\- Any PoC or patch if available



We aim to acknowledge all reports within 72 hours and provide a timeline for remediation.



\---



\## Supported Versions



This repository is a multi-project prototype. For security-sensitive deployments, prefer the latest commit on `main`.



\---



\## Disclosure Policy



\- We follow coordinated disclosure. We will work with the reporter to fix vulnerabilities before public disclosure.

\- Typical timeline: Acknowledge within 72 hours, mitigation or fix within 90 days where reasonable.



\---



\## Hardening \& Recommendations (for deployers)



\- Never expose the backend to the public Internet without a secure tunnel and webhook validation.

\- Validate all inbound webhooks (e.g., Twilio) using signature validation.

\- Require human approvals for all critical actions and keep audit logs.

\- Verify downloaded model artifacts with checksums (SHA256) and store checksums in a signed manifest when possible.

\- Use HTTPS for all external downloads and validate certificates.

\- Limit remote control features (WhatsApp/Twilio) to authenticated, documented flows; do not auto-execute commands from remote messages.



\---



\## Disclosure Contact



contact@alexkoncept.com



\---



\# Politique de sécurité (extrait français)



Merci de contribuer à la sécurité d'Orba OS. Pour signaler une vulnérabilité : contactez contact@alexkoncept.com en précisant le composant, reproduction, impact et PoC si possible. Nous accusons réception sous 72h et visons un correctif dans un délai raisonnable.

