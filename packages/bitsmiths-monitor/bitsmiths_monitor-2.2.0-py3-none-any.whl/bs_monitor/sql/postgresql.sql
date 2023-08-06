CREATE TABLE monitor.batch (
   id SERIAL8
  ,parent_id BIGINT
  ,name varchar(256)
  ,group_id varchar(128)
  ,status character(1)
  ,CYCLE character(1)
  ,run_date TIMESTAMP
  ,run_interval INTEGER
  ,run_time varchar(6)
  ,ext_data JSONB
  ,stamp_by varchar(128)
  ,stamp_tm TIMESTAMP
);
ALTER TABLE monitor.batch ADD PRIMARY KEY (
   id
);
CREATE TABLE monitor.jobinstmetric (
   jobinst_id BIGINT
  ,stamp_tm TIMESTAMP
  ,mtype character(1)
  ,msg VARCHAR
);
CREATE TABLE monitor.jobinst (
   id SERIAL8
  ,parent_id BIGINT
  ,job_id BIGINT
  ,batchinst_id BIGINT
  ,process_date TIMESTAMP
  ,priority INTEGER
  ,status character(1)
  ,extra_args varchar(256)
  ,group_job varchar(128)
  ,group_batch varchar(128)
  ,stamp_by varchar(128)
  ,stamp_tm TIMESTAMP
);
ALTER TABLE monitor.jobinst ADD PRIMARY KEY (
   id
);
CREATE TABLE monitor.mondate (
   id varchar(16)
  ,descr VARCHAR
  ,value DATE
  ,stamp_by varchar(128)
  ,stamp_tm TIMESTAMP
);
ALTER TABLE monitor.mondate ADD PRIMARY KEY (
   id
);
CREATE TABLE monitor.job (
   id SERIAL8
  ,name varchar(256)
  ,group_id varchar(128)
  ,program_path varchar(256)
  ,program_args varchar(256)
  ,priority INTEGER
  ,stamp_by varchar(128)
  ,stamp_tm TIMESTAMP
);
ALTER TABLE monitor.job ADD PRIMARY KEY (
   id
);
CREATE TABLE monitor.batchitem (
   id BIGINT
  ,batch_id BIGINT
  ,job_id BIGINT
  ,extra_args varchar(128)
  ,stamp_by varchar(128)
  ,stamp_tm TIMESTAMP
);
ALTER TABLE monitor.batchitem ADD PRIMARY KEY (
   id
  ,batch_id
);
CREATE TABLE monitor.jobinstcancel (
   jobinst_id BIGINT
  ,reason VARCHAR
  ,stamp_by varchar(128)
  ,stamp_tm TIMESTAMP
);
ALTER TABLE monitor.jobinstcancel ADD PRIMARY KEY (
   jobinst_id
);
CREATE TABLE monitor.batchinst (
   id SERIAL8
  ,parent_id BIGINT
  ,batch_id BIGINT
  ,status character(1)
  ,run_date TIMESTAMP
  ,start_date TIMESTAMP
  ,end_date TIMESTAMP
);
ALTER TABLE monitor.batchinst ADD PRIMARY KEY (
   id
);
ALTER TABLE monitor.batchinst
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN run_date SET NOT NULL
;
ALTER TABLE monitor.batchinst ADD CONSTRAINT batchinst_fk_parent FOREIGN KEY (parent_id) REFERENCES monitor.batchinst;
ALTER TABLE monitor.batchinst ADD CONSTRAINT batchinst_fk_batch FOREIGN KEY (batch_id) REFERENCES monitor.batch;
ALTER TABLE monitor.jobinst
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN job_id SET NOT NULL
  ,ALTER COLUMN process_date SET NOT NULL
  ,ALTER COLUMN priority SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN group_job SET NOT NULL
  ,ALTER COLUMN stamp_by SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
;
ALTER TABLE monitor.jobinst ADD CONSTRAINT jobinst_fk_jobinst FOREIGN KEY (parent_id) REFERENCES monitor.jobinst;
ALTER TABLE monitor.jobinst ADD CONSTRAINT jobinst_fk_job FOREIGN KEY (job_id) REFERENCES monitor.job;
ALTER TABLE monitor.jobinst ADD CONSTRAINT jobinst_fk_batchinst FOREIGN KEY (batchinst_id) REFERENCES monitor.batchinst;
ALTER TABLE monitor.jobinstcancel
   ALTER COLUMN jobinst_id SET NOT NULL
  ,ALTER COLUMN stamp_by SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
;
ALTER TABLE monitor.jobinstcancel ADD CONSTRAINT jobinstcancel_fk_jobinst FOREIGN KEY (jobinst_id) REFERENCES monitor.jobinst;
ALTER TABLE monitor.mondate
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN value SET NOT NULL
  ,ALTER COLUMN stamp_by SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
;
ALTER TABLE monitor.batch
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN name SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN CYCLE SET NOT NULL
  ,ALTER COLUMN run_date SET NOT NULL
  ,ALTER COLUMN run_interval SET NOT NULL
  ,ALTER COLUMN stamp_by SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
;
ALTER TABLE monitor.batch ADD CONSTRAINT batch_fk_batch FOREIGN KEY (parent_id) REFERENCES monitor.batch;
ALTER TABLE monitor.batch ADD CONSTRAINT batch_uk_name UNIQUE (
   name
);
ALTER TABLE monitor.jobinstmetric
   ALTER COLUMN jobinst_id SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
  ,ALTER COLUMN mtype SET NOT NULL
;
ALTER TABLE monitor.jobinstmetric ADD CONSTRAINT jobinstmetric_fk_jobinst FOREIGN KEY (jobinst_id) REFERENCES monitor.jobinst;
ALTER TABLE monitor.batchitem
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN batch_id SET NOT NULL
  ,ALTER COLUMN job_id SET NOT NULL
  ,ALTER COLUMN stamp_by SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
;
ALTER TABLE monitor.batchitem ADD CONSTRAINT batchitem_fk_batch FOREIGN KEY (batch_id) REFERENCES monitor.batch;
ALTER TABLE monitor.batchitem ADD CONSTRAINT batchitem_fk_job FOREIGN KEY (job_id) REFERENCES monitor.job;
ALTER TABLE monitor.job
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN name SET NOT NULL
  ,ALTER COLUMN group_id SET NOT NULL
  ,ALTER COLUMN program_path SET NOT NULL
  ,ALTER COLUMN priority SET NOT NULL
  ,ALTER COLUMN stamp_by SET NOT NULL
  ,ALTER COLUMN stamp_tm SET NOT NULL
;
ALTER TABLE monitor.job ADD CONSTRAINT job_uk_name UNIQUE (
   name
);
CREATE INDEX batchitem_ix_batch ON monitor.batchitem
(
   batch_id
);
CREATE INDEX batchitem_ix_job ON monitor.batchitem
(
   job_id
);
CREATE INDEX batch_ix_parent ON monitor.batch
(
   parent_id
);
CREATE INDEX batchinst_ix_parent ON monitor.batchinst
(
   parent_id
);
CREATE INDEX batchinst_ix_batch ON monitor.batchinst
(
   batch_id
  ,run_date
  ,status
);
CREATE INDEX jobinstmetric_ix_jobinst ON monitor.jobinstmetric
(
   jobinst_id
);
CREATE INDEX jobinst_ix_proc ON monitor.jobinst
(
   process_date
  ,priority
  ,status
  ,group_job
);
CREATE INDEX jobinst_ix_parent ON monitor.jobinst
(
   parent_id
);
CREATE INDEX jobinst_ix_job ON monitor.jobinst
(
   job_id
);
CREATE INDEX jobinst_ix_batchinst ON monitor.jobinst
(
   batchinst_id
);
INSERT INTO monitor.mondate SELECT 'go-live',  'Go Live Date',   CURRENT_DATE, '[monitor]', CURRENT_TIMESTAMP;
INSERT INTO monitor.mondate SELECT 'rundate',  'System Rundate', CURRENT_DATE, '[monitor]', CURRENT_TIMESTAMP;
INSERT INTO monitor.mondate SELECT 'check-in', 'Monitor Manager Check-In', CURRENT_DATE, '[monitor]', CURRENT_TIMESTAMP;
