BEGIN;
PREPARE p9_task (STRING, STRING, JSONB, BYTES, BYTES) AS
  INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)
  VALUES ($1,$2,$3,$4,$5);
EXECUTE p9_task('ck-p9-live-refuse-r1','ck-p9-completion-r1','{"kind":"task","trial":"ck-p9-live-refuse-r1"}',decode('ae6d1534e88c649b923405c60f477bf409df6aa116d749e1bdc15f66eeda71ef','hex'),decode('cccc1e0187a8e1d310f7639d36c88d34591b9367f0242d7c50d5d3893924308b','hex'));
DEALLOCATE p9_task;
PREPARE p9_event (STRING, STRING, INT8, BYTES, BYTES, JSONB, BYTES) AS
  INSERT INTO ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7);
EXECUTE p9_event('ck-p9-live-refuse-r1-event-r1','ck-p9-live-refuse-r1',0,decode('0000000000000000000000000000000000000000000000000000000000000000','hex'),decode('cccc1e0187a8e1d310f7639d36c88d34591b9367f0242d7c50d5d3893924308b','hex'),'{"kind":"event","trial":"ck-p9-live-refuse-r1"}',decode('aebce260d27cd13f6d19d882f2987c5d74ad2397b120f123374e52d07e612ac9','hex'));
DEALLOCATE p9_event;
PREPARE p9_receipt (BYTES, STRING, BYTES, STRING, JSONB) AS
  INSERT INTO ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json)
  VALUES ($1,$2,$3,$4,$5);
EXECUTE p9_receipt(decode('b6d0fe2e5b004d67c3eea7ebc2ffb45d4defcd6184ec670f068915792aa884d8','hex'),'ck-p9-live-refuse-r1',decode('aebce260d27cd13f6d19d882f2987c5d74ad2397b120f123374e52d07e612ac9','hex'),'SEALED','{"kind":"receipt","trial":"ck-p9-live-refuse-r1"}');
DEALLOCATE p9_receipt;
PREPARE p9_vector (STRING, STRING, BYTES, STRING, VECTOR(64), BYTES) AS
  INSERT INTO ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest)
  VALUES ($1,$2,$3,$4,$5,$6);
EXECUTE p9_vector('ck-p9-live-refuse-r1-vector-r1','ck-p9-live-refuse-r1',decode('aebce260d27cd13f6d19d882f2987c5d74ad2397b120f123374e52d07e612ac9','hex'),'ck-p9-completion','[0.000000,0.000000,0.000000,0.000000,0.000000,0.273674,0.000000,0.000000,0.000000,0.000000,0.000000,0.272675,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.453460,0.000000,0.000000,0.000000,0.000000,0.413508,0.000000,0.000000,0.000000,0.000000,0.000000,0.331605,0.000000,-0.344590,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.495410,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000]'::VECTOR(64),decode('b72c08c01327f9f38a6c4e62dbe803721099b4369af7ffc851453d814096b4cb','hex'));
DEALLOCATE p9_vector;
COMMIT;
