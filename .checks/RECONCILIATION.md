# Apps production reconciliation

This branch starts from existing PR #5 at 2e41a68c2e9fdcf7394bacf539932a9b19d11e34, preserving its five newer public pages exactly. PR #5 is owned by sorcerai, last updated 2026-09-24, and main remains 772f718bc21fa6635b395dc9e75e4d691763ce4b at the 2026-10-02 read. The original PR and production are untouched.

Production deployment 1077a6e6-8624-49ba-8b65-c0c5ae93cb8f has an empty source field. Its five newer pages exactly match PR #5; older pages are a mixed tree, with central intent attribution removed and absolute spend/provisioning claims restored. There is no verified single source commit for production.

The candidate retains PR #5's commercial pages, refreshed SKAN article and sitemap. It restores the intended existing attribution and cautious copy by using PR #5's full tree, which incorporates main's changes: illustrative UA radar, platform-set ceilings, case-specific provisioning and no guaranteed cutover timing. The remaining absolute homepage metadata promise is replaced with a request to review options. No new benefits or pricing are introduced.

The five newer pages intentionally retain their exact bytes, including their existing attribution coverage. Expanding analytics on these pages requires separate review and is not part of this reconciliation.

Tests execute WhatsApp navigation with SDK present/absent, nested clicks and desktop/mobile viewports. Central-intent tests intercept external requests and verify attribution payload bounds and navigation when sendBeacon succeeds, throws or is missing. Preserved-page hashes represent the explicit public-byte preservation contract. CI never sends analytics or opens real WhatsApp.

Do not merge or deploy this branch automatically. Preview exact output, compare against the preserved production archive, and review copy before choosing the eventual replacement for PR #5. Local snapshots are in the task-6 apps-live-preservation directory and archive, not uploaded to this repository.
