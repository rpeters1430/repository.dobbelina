# Upstream commit review (Nov 2025)

The table below reviews commits on `upstream/master` that are not yet included on this fork (`work`). Version-bump packaging commits are marked as not needed. The **Fork status / action** column captures what we already covered locally versus items to cherry-pick now.

| Commit | Upstream title | Key changes | Recommendation | Fork status / action |
| --- | --- | --- | --- | --- |
| f3d48c1 | xhmster playback | Major XHamster decrypter and site playback changes plus changelog. | **Merge** – functional fix. | Fork currently working; optional cherry-pick after reviewing diffs for stability gains. |
| 1721e03 | terebon - fix playback | Refines Terebon playback handling and changelog. | **Merge** – functional fix. | Unsure if already covered – compare with fork changes; cherry-pick if behavior still off. |
| d47192d | camsoda #1685 | Small Camsoda update. | **Merge** – functional fix. | Not sure of fork state – review and cherry-pick if our Camsoda differs. |
| 86d995a | hanime fixes #1686 | Adds minor Hanime adjustments and changelog entry. | **Merge** – functional fix. | Missing here – cherry-pick with 60b6859 for complete fix set. |
| 5f247bf | 2025-11-02 Bumped to v.1.1.157 | Metadata and packaged zip only. | Skip – version bump only. | Skip. |
| 0e6bbc7 | 2025-11-02 Bumped to v.1.1.157 | Packaged zip only (code already in functional commits below). | Skip – version bump only. | Skip. |
| 60b6859 | hanime playback - fixes #1688 | Adjusts Hanime playback logic and changelog. | **Merge** – functional fix. | Missing here – cherry-pick along with 86d995a. |
| 71d1398 | vintagetube - removed | Removes VintageTube provider and metadata. | **Merge** – content removal reflected in code. | Already removed in fork – no action. |
| 27419a0 | 2025-11-09 Bumped to v.1.1.158 | Metadata and packaged zip only. | Skip – version bump only. | Skip. |
| 9722f3e | camwhoresbay - fix next page | Reworks CamWhoresBay pagination; expands changelog. | **Merge** – functional fix. | Not done here; cherry-pick with b4beb80 to restore pagination. |
| d4ee4fc | 2025-11-16 Bumped to v.1.1.159 | Metadata and packaged zip only. | Skip – version bump only. | Skip. |
| 67bd60f | tokyomotion - new site | Introduces TokyoMotion site module plus metadata. | **Merge** – new site support. | Already added in fork – no action. |
| a34c0a7 | terebon - fix listing | Updates Terebon listing logic and changelog. | **Merge** – functional fix. | Unsure if our recent work fully fixed – verify against fork; cherry-pick if gaps remain. |
| e40d58d | camcaps site name change | Renames CamCaps to SimpVids references. | **Merge** – functional rename. | Already handled in fork – no action. |
| 4787d5f | 2025-11-23 Bumped to v.1.1.160 | Metadata and packaged zip only. | Skip – version bump only. | Skip. |
| 122e955 | freepornvideos - new site | Adds FreePornVideos site module, assets, and changelog entry. | **Merge** – new site support. | Missing on fork – cherry-pick to add site. |
| b8e1df5 | 2025-11-30 Bumped to v.1.1.161 | Metadata and packaged zip only. | Skip – version bump only. | Skip. |
| d522ced | awmnet - fix listing | Repairs listing logic and updates changelog entries for AWMnet. | **Merge** – functional fix. | Not done here; fork instance is broken – cherry-pick. |
| b4beb80 | camwhoresbay - fix playback | Adjusts CamWhoresBay playback handling and updates changelog. | **Merge** – functional fix. | Not done here; fork’s CamWhoresBay is broken – cherry-pick both CamWhoresBay fixes (with 9722f3e) together. |

## Notes
- Packaging/version-bump commits (zip + metadata only) are unnecessary because the fork builds its own packages.
- Functional commits above may need conflict resolution against local refactors on `work`, especially in site modules updated by our modernization efforts.
