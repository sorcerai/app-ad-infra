# Local resource verification

Install the CI-pinned `playwright==1.55.0` and Chromium, then run:

```sh
python -m unittest discover -s .checks -p 'test_contract.py' -v
```

`PLAYWRIGHT_EXECUTABLE_PATH` optionally selects an installed Chromium binary.
The tests serve local HTML, intercept WhatsApp destinations and block production
analytics/intent requests. Existing secondary-page inquiry contracts run with
and without a synthetic SDK. Resource tests check real navigation, rendered
headings, canonical/schema agreement, FAQ agreement and mobile width.

The replacement retains the existing extensionless resource URL. On 3 October
2026, read-only deployed checks returned 308 from `/resources/index` to
`/resources/`, and 200 at `/resources/`; no new redirect rule was needed.

Content provenance: `AdsInfra_Satellite_Content_Drafts.docx`, Library identity
`libfile_c5341d7364288191972c30716e8e9713`, article 1 and its editor/source ledger.
The downloaded pack was 75,627 bytes and readable as DOCX. Primary source links
remain in the public article. Google's documented fine/coarse distinction was
rechecked on 3 October 2026. The arithmetic example is invented, not client proof.

Before publishing: a measurement implementer must review the guidance against
the actual supported SDK/network combination, and the business owner must confirm
service scope. No customer configuration was inspected. Dates in the copy record
source review; deployment has not occurred. Related audit-tool promotion is held
pending claim review; its public route remains available. This PR changes no offer,
recipient, analytics access or tracking implementation.

## Public deployment export

Run `npm run build` to create `.public-dist` from the explicit
`scripts/public-assets.json` allowlist. `npm run deploy` builds first and uploads
only that directory. Wrangler's configured default output is also `.public-dist`.
Do not run `wrangler pages deploy .`: an explicit root argument bypasses the export.
Review allowlist additions as public content. Tests, CI, source helpers, repository
configuration and credentials must remain outside the allowlist. The exporter
refuses dot-prefixed allowlist path segments, missing or symlinked sources and unexpected preexisting output files.
Run `node --test .checks/test_export.mjs` for executable export checks.
The existing postdeploy IndexNow hook remains unchanged; building/testing does
not invoke it or publish anything.
