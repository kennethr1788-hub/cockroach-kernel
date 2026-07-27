# Hardening Gate 2 Secret Handoff Attempt R1

- `UTC_RECORDED`: `2026-07-27T17:53:43Z`
- `RESULT`: `FAILED_BEFORE_SECRET_CREATION`
- `FAILURE_CLASS`: `INTERACTIVE_GETPASS_BINDING_NOT_REPLACED`
- `AWS_SECRET_AFTER_ATTEMPT`: `absent`
- `CLIPBOARD_AFTER_ATTEMPT_BYTES`: `0`
- `CREDENTIAL_PRINTED_OR_LOGGED`: `no`
- `AWS_PUBLIC_ENDPOINT_EXISTS`: `no`

The executor attempted to invoke the existing hidden-prompt helper through an
ephemeral wrapper because the CUA inventory showed that Terminal was a shared
single process with two active project windows. The wrapper changed a copied
namespace rather than the function's actual global `getpass` binding. The
helper reached the password prompt and stopped at EOF before constructing or
submitting an AWS secret request.

The shell then cleared the clipboard unconditionally. A metadata-only AWS
Secrets Manager readback confirmed `ck-hardening-demo-db` remained absent. No
credential bytes appeared in argv, stdout, stderr, a file, a receipt, source,
or tool output.

The repair adds an explicit project-local `--clipboard` mode. It reads the
provider-generated value through `/usr/bin/pbpaste`, retains the same length
and NUL checks, sends the fixed secret request through AWS CLI stdin, suppresses
provider output, and leaves clipboard clearing to the enclosing closeout step.
