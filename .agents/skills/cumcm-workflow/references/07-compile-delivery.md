# Delivery responsibility

Delivery is a `finalizing` responsibility. It uses only current user-supplied official rules/templates and the fresh `paper-delivery` handoff.

## Hard checks

- the selected compile attempt exited successfully with the declared engine;
- the reviewed PDF path/hash, page count, layout review, compile receipt, and delivery manifest agree;
- the compile receipt contains a current `sha256-tree-v1` snapshot of every required editable LaTeX source file and its entry point;
- fonts/glyphs, overflow, clipping, unreadable figures/tables, and unresolved references are checked;
- current official-format compliance is verified from user-supplied material;
- final PDF, editable LaTeX source, and computation source are separately addressable and present.

The exact PDF hash and source-tree snapshot bind the final approved artifact to its editable source without requiring per-file hashes to be typed or reviewed manually. Ordinary logs, caches, temporary files, documentation, and debugging material stay outside the delivery package.

Missing current rules or a required template yields `blocked_missing_user_material`; it does not authorize web search. Submission remains user-controlled.
