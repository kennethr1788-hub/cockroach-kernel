BEGIN;
PREPARE p9_task (STRING, STRING, JSONB, BYTES, BYTES) AS
  INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)
  VALUES ($1,$2,$3,$4,$5);
EXECUTE p9_task('ck-p9-live-promote-r1','ck-p9-completion-r1','{"kind":"task","trial":"ck-p9-live-promote-r1"}',decode('576e205d85d5d55bd9f9586ddeb49698606fac2820b74a384315589aa7e2d379','hex'),decode('174bd8e7e126833072d28e812e48bf0cec3abe9a3b028a6ce340eaf0550c565a','hex'));
DEALLOCATE p9_task;
PREPARE p9_event (STRING, STRING, INT8, BYTES, BYTES, JSONB, BYTES) AS
  INSERT INTO ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7);
EXECUTE p9_event('ck-p9-live-promote-r1-event-r1','ck-p9-live-promote-r1',0,decode('0000000000000000000000000000000000000000000000000000000000000000','hex'),decode('174bd8e7e126833072d28e812e48bf0cec3abe9a3b028a6ce340eaf0550c565a','hex'),'{"kind":"event","trial":"ck-p9-live-promote-r1"}',decode('86c994860c7cef848aa4190951e6cd9353358c5a1fa8245b07033469a8aedcbd','hex'));
DEALLOCATE p9_event;
PREPARE p9_receipt (BYTES, STRING, BYTES, STRING, JSONB) AS
  INSERT INTO ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json)
  VALUES ($1,$2,$3,$4,$5);
EXECUTE p9_receipt(decode('2f30d74734954eab00ceee936c9996bc8a0881b55ee7027b2decccd4a0d6a8bc','hex'),'ck-p9-live-promote-r1',decode('86c994860c7cef848aa4190951e6cd9353358c5a1fa8245b07033469a8aedcbd','hex'),'SEALED','{"kind":"receipt","trial":"ck-p9-live-promote-r1"}');
DEALLOCATE p9_receipt;
PREPARE p9_vector (STRING, STRING, BYTES, STRING, VECTOR(64), BYTES) AS
  INSERT INTO ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest)
  VALUES ($1,$2,$3,$4,$5,$6);
EXECUTE p9_vector('ck-p9-live-promote-r1-vector-r1','ck-p9-live-promote-r1',decode('86c994860c7cef848aa4190951e6cd9353358c5a1fa8245b07033469a8aedcbd','hex'),'ck-p9-completion','[0.000000,0.000000,0.000000,0.000000,0.000000,0.277759,0.000000,0.000000,0.000000,0.000000,-0.382172,0.276745,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.460229,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.336555,0.000000,-0.349733,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.502805,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000]'::VECTOR(64),decode('d4a7e070ddd272ab040436d561edbb3ea88f0b2367515bfbf2cf418402a03271','hex'));
DEALLOCATE p9_vector;
COMMIT;
