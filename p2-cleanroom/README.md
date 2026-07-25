# P2 clean-room fixture

This directory is a synthetic, offline fixture. It is not connected to a
CockroachDB cluster and contains no credentials. The migration is a contract
input for the later disposable database harness.

Required future commands must create a temporary database/root, apply the
migration, load the fixture, run rollback, delete the temporary root, and scan
for residue. They must not read or write HOME or live memory state.
