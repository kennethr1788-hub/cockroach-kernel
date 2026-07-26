BEGIN;
PREPARE p9_worker (STRING,STRING,STRING,BYTES,BYTES,INT8,STRING,STRING,JSONB,BYTES) AS
  INSERT INTO ck.worker_results(request_id,task_id,candidate_id,request_hash,response_hash,attempt,supersedes,status,result_json,result_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10);
EXECUTE p9_worker('ck-p9-live-promote-request-r1','ck-p9-live-promote-r1','ck-p9-live-promote-candidate-r1',decode('3c7d6d1bb56f5a3901dbfab9e83a0c1c5fb3d2e9fc8702986f0d5c10daae15ec','hex'),decode('d67f70944096a79c427e2086ed3bac723bef071ae3f5d21e70dcaa3eaeeb51f2','hex'),1,NULL,'ADVISORY','{"aws_request_id_hash":"1fa2bad5f4b71b841374730bff93b8b810b1fb71bba35c4d7e62430fe0c8d2ef","request_hash":"3c7d6d1bb56f5a3901dbfab9e83a0c1c5fb3d2e9fc8702986f0d5c10daae15ec","request_id":"ck-p9-live-promote-request-r1","response_hash":"d67f70944096a79c427e2086ed3bac723bef071ae3f5d21e70dcaa3eaeeb51f2","status":"ADVISORY","version":"p9-live-worker-result-v1"}',decode('0489b0249c3eaa6081cdfa0576d460d583f9c71d9639a65d44cd55cb4438c979','hex'));
DEALLOCATE p9_worker;
PREPARE p9_projection (STRING,STRING,STRING,BYTES,INT8,JSONB,BYTES) AS
  INSERT INTO ck.projection_events(projection_id,source_table,source_key,receipt_hash,sequence,projected_json,projection_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7);
EXECUTE p9_projection('ck-p9-live-promote-r1-projection-r1','worker_results','ck-p9-live-promote-request-r1',decode('2f30d74734954eab00ceee936c9996bc8a0881b55ee7027b2decccd4a0d6a8bc','hex'),1,'{"receipt_hash":"2f30d74734954eab00ceee936c9996bc8a0881b55ee7027b2decccd4a0d6a8bc","request_id":"ck-p9-live-promote-request-r1","result_hash":"0489b0249c3eaa6081cdfa0576d460d583f9c71d9639a65d44cd55cb4438c979","version":"p9-live-projection-v1"}',decode('05038784019e86388554f94e4f6757de96cdc82256d1937f7dc2dc63bd3682d8','hex'));
DEALLOCATE p9_projection;
COMMIT;
