# Workflows

You're installed. You've done something. You've seen the pieces.

Now you're working. Every day. Your harness does the typing. You do the supervising.

## The daily loop

```
search → inspect → run → audit
```

Find what exists. Check whether you can afford it, right now. Do the thing. Read what actually happened. That's the whole working rhythm — everything else is depth on one of these four words.

## Pick your problem

| You're trying to… | Go to |
|---|---|
| Find what exists — or discover the gap where it should be | [discover.md](discover.md) |
| Read and write your actual data | [query-data.md](query-data.md) |
| Turn repeated work into governed routines | [routines.md](routines.md) |
| Talk to Stripe, GitHub, Twilio | [apis.md](apis.md) |
| Wake routines on schedules, webhooks, and HTTP | [triggers.md](triggers.md) |
| Get a human decision mid-flight | [approvals.md](approvals.md) |

## The shared rhythm

Every workflow in this section runs on the same physics:

- **Reads are free.** Bounded, but free.
- **Writes need `-m`.** Every mutation declares intent or it doesn't happen — the full contract lives in [query-data.md](query-data.md).
- **Denials teach.** Every `exit 2` arrives with the rule it broke, the state it left untouched, and a remedy — decoded in [reference/exit-codes.md](../reference/exit-codes.md).

Learn the rhythm once. It holds everywhere, from raw SQL to Stripe calls to cron schedules.

**Start with discovery** → [discover.md](discover.md)
