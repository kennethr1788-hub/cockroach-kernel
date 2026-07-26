BEGIN;
PREPARE p9_worker (STRING,STRING,STRING,BYTES,BYTES,INT8,STRING,STRING,JSONB,BYTES) AS
  INSERT INTO ck.worker_results(request_id,task_id,candidate_id,request_hash,response_hash,attempt,supersedes,status,result_json,result_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10);
EXECUTE p9_worker('ck-p9-live-refuse-request-r1','ck-p9-live-refuse-r1','ck-p9-live-refuse-candidate-r1',decode('07e049a9e3552aa5ead493cd728a81d190ddda26c35b77a22d99b3e78665e779','hex'),decode('4212a2cc26fe4fd7623ba80b8c9d2444d261c4d252d9be673e065b43ceac35ad','hex'),1,NULL,'ADVISORY','{"aws_request_id_hash":"e1ee41bb92bb02718840ecea1532510ecf5e1285394f405c0b3ce17a7f917666","request_hash":"07e049a9e3552aa5ead493cd728a81d190ddda26c35b77a22d99b3e78665e779","request_id":"ck-p9-live-refuse-request-r1","response_hash":"4212a2cc26fe4fd7623ba80b8c9d2444d261c4d252d9be673e065b43ceac35ad","status":"ADVISORY","version":"p9-live-worker-result-v1"}',decode('c84d932b66ca0dc749029e8c7970efa626940b447f85ed9f7c57dfb77462bfe3','hex'));
DEALLOCATE p9_worker;
PREPARE p9_projection (STRING,STRING,STRING,BYTES,INT8,JSONB,BYTES) AS
  INSERT INTO ck.projection_events(projection_id,source_table,source_key,receipt_hash,sequence,projected_json,projection_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7);
EXECUTE p9_projection('ck-p9-live-refuse-r1-projection-r1','worker_results','ck-p9-live-refuse-request-r1',decode('b6d0fe2e5b004d67c3eea7ebc2ffb45d4defcd6184ec670f068915792aa884d8','hex'),1,'{"receipt_hash":"b6d0fe2e5b004d67c3eea7ebc2ffb45d4defcd6184ec670f068915792aa884d8","request_id":"ck-p9-live-refuse-request-r1","result_hash":"c84d932b66ca0dc749029e8c7970efa626940b447f85ed9f7c57dfb77462bfe3","version":"p9-live-projection-v1"}',decode('ca7529e66618773d5d12594b8e14304183c4db85da2f76891c04d9d0379102ac','hex'));
DEALLOCATE p9_projection;
COMMIT;
