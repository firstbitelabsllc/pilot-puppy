# A/B/C decisions

In the browser, this appears as **Pick what happens next**. It is simply a
multiple-choice question with three next-step buttons—not a model picker, a
router, or a coding command. Nothing starts until the person chooses.

A plan in `needs_input` state declares one question and exactly three bounded
options. Each option has an ID, label, and consequence. The browser sends only:

```json
{"plan":"project/PLAN.md","option_id":"cold-review","revision":7}
```

The server compares that revision with current authority. A current choice is
`received`; a stale choice is `superseded`; a mismatched choice is
`not_delivered`. Receipt does not mean the coding host applied the choice.
