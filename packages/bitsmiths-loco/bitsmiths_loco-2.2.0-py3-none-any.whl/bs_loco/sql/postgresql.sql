CREATE TABLE loco.msghist (
   id BIGINT
  ,status character(1)
  ,msgdate TIMESTAMP
  ,msg JSONB
);
ALTER TABLE loco.msghist ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.msg (
   id SERIAL8
  ,msgreq_id BIGINT
  ,corrtype_id varchar(16)
  ,notype_id varchar(128)
  ,priority INTEGER
  ,status character(1)
  ,retry_cnt INTEGER
  ,fail_cnt INTEGER
  ,time_sent TIMESTAMP
  ,time_taken numeric(15,6)
  ,corrprov_id varchar(16)
  ,msglog JSONB
  ,payload JSONB
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.msg ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.corrprov (
   id varchar(16)
  ,corrtype_id varchar(16)
  ,descr VARCHAR
  ,status character(1)
  ,cfg_schema JSONB
  ,cfg JSONB
  ,lastcfg_id BIGINT
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.corrprov ADD PRIMARY KEY (
   id
  ,corrtype_id
);
CREATE TABLE loco.nores (
   id varchar(128)
  ,filename varchar(256)
  ,mimetype varchar(128)
  ,content BYTEA
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.nores ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.nodict (
   id varchar(128)
  ,value varchar(256)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.nodict ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.notempl (
   notype_id varchar(128)
  ,corrtype_id varchar(16)
  ,status character(1)
  ,lastcfg_id BIGINT
  ,templ JSONB
  ,res_list JSONB
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.notempl ADD PRIMARY KEY (
   notype_id
  ,corrtype_id
);
CREATE TABLE loco.snapprov (
   valuedate DATE
  ,corrtype_id varchar(16)
  ,corrprov_id varchar(16)
  ,msg_sent INTEGER
  ,msg_failed INTEGER
  ,msg_retry INTEGER
  ,avg_msgtime numeric(15,6)
  ,tot_msgtime numeric(15,6)
);
ALTER TABLE loco.snapprov ADD PRIMARY KEY (
   valuedate
  ,corrtype_id
  ,corrprov_id
);
CREATE TABLE loco.msgreq (
   id SERIAL8
  ,notype_id varchar(128)
  ,priority INTEGER
  ,status character(1)
  ,time_req TIMESTAMP
  ,time_to_send TIMESTAMP
  ,time_proc TIMESTAMP
  ,msg_addr JSONB
  ,msg_dict JSONB
  ,cust_res BOOLEAN
  ,meta_data JSONB
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.msgreq ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.corrtypeallow (
   corrtype_id varchar(16)
  ,allow_id varchar(32)
  ,status character(1)
  ,regex varchar(256)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.corrtypeallow ADD PRIMARY KEY (
   corrtype_id
  ,allow_id
);
CREATE TABLE loco.snapmsgreq (
   valuedate DATE
  ,notype_id varchar(64)
  ,tot_req INTEGER
  ,tot_proc INTEGER
  ,tot_cancelled INTEGER
  ,tot_part_canc INTEGER
  ,tot_msgs INTEGER
  ,tot_msgs_sent INTEGER
  ,tot_msgs_failed INTEGER
  ,tot_msgs_retrys INTEGER
);
ALTER TABLE loco.snapmsgreq ADD PRIMARY KEY (
   valuedate
  ,notype_id
);
CREATE TABLE loco.msgreqres (
   id SERIAL8
  ,msgreq_id BIGINT
  ,corr_id_list JSONB
  ,filename VARCHAR
  ,mimetype VARCHAR
  ,content BYTEA
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.msgreqres ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.corrprovcfg (
   id SERIAL8
  ,corrtype_id varchar(16)
  ,corrprov_id varchar(16)
  ,status character(1)
  ,notes varchar(4096)
  ,activate TIMESTAMP
  ,deactivate TIMESTAMP
  ,cfg JSONB
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.corrprovcfg ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.config (
   id VARCHAR
  ,descr VARCHAR
  ,value VARCHAR
  ,grp VARCHAR
  ,modified_by VARCHAR
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.config ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.notemplcfg (
   id SERIAL8
  ,notype_id varchar(128)
  ,corrtype_id varchar(16)
  ,status character(1)
  ,activate TIMESTAMP
  ,deactivate TIMESTAMP
  ,templ JSONB
  ,res_list JSONB
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.notemplcfg ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.corrtype (
   id varchar(16)
  ,descr VARCHAR
  ,status character(1)
  ,templ_schema JSONB
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.corrtype ADD PRIMARY KEY (
   id
);
CREATE TABLE loco.notype (
   id varchar(128)
  ,status character(1)
  ,descr varchar(256)
  ,grp varchar(64)
  ,priority INTEGER
  ,pref_corr JSONB
  ,corr_cnt INTEGER
  ,max_life INTEGER
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE loco.notype ADD PRIMARY KEY (
   id
);
ALTER TABLE loco.corrtype
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN templ_schema SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.corrprovcfg
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN corrtype_id SET NOT NULL
  ,ALTER COLUMN corrprov_id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN activate SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.corrprovcfg ADD CONSTRAINT corrprovcfg_fk_corrprov FOREIGN KEY (corrtype_id, corrprov_id) REFERENCES loco.corrprov;
ALTER TABLE loco.notype
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN grp SET NOT NULL
  ,ALTER COLUMN priority SET NOT NULL
  ,ALTER COLUMN corr_cnt SET NOT NULL
  ,ALTER COLUMN max_life SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.msgreqres
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN msgreq_id SET NOT NULL
  ,ALTER COLUMN corr_id_list SET NOT NULL
  ,ALTER COLUMN filename SET NOT NULL
  ,ALTER COLUMN content SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.msgreqres ADD CONSTRAINT msgreqres_fk_msgreq FOREIGN KEY (msgreq_id) REFERENCES loco.msgreq;
ALTER TABLE loco.msghist
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN msgdate SET NOT NULL
  ,ALTER COLUMN msg SET NOT NULL
;
ALTER TABLE loco.corrprov
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN corrtype_id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.corrprov ADD CONSTRAINT corrprov_fk_corrtype FOREIGN KEY (corrtype_id) REFERENCES loco.corrtype;
ALTER TABLE loco.corrprov ADD CONSTRAINT corrprov_fk_cfg FOREIGN KEY (lastcfg_id) REFERENCES loco.corrprovcfg;
ALTER TABLE loco.notempl
   ALTER COLUMN notype_id SET NOT NULL
  ,ALTER COLUMN corrtype_id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN templ SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.notempl ADD CONSTRAINT notempl_fk_notype FOREIGN KEY (notype_id) REFERENCES loco.notype;
ALTER TABLE loco.notempl ADD CONSTRAINT notempl_fk_corrtype FOREIGN KEY (corrtype_id) REFERENCES loco.corrtype;
ALTER TABLE loco.notempl ADD CONSTRAINT notempl_fk_cfg FOREIGN KEY (lastcfg_id) REFERENCES loco.notemplcfg;
ALTER TABLE loco.msg
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN msgreq_id SET NOT NULL
  ,ALTER COLUMN priority SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN retry_cnt SET NOT NULL
  ,ALTER COLUMN fail_cnt SET NOT NULL
  ,ALTER COLUMN time_taken SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.msg ADD CONSTRAINT msg_fk_msgreq FOREIGN KEY (msgreq_id) REFERENCES loco.msgreq;
ALTER TABLE loco.msg ADD CONSTRAINT msg_fk_corrtype FOREIGN KEY (corrtype_id) REFERENCES loco.corrtype;
ALTER TABLE loco.msg ADD CONSTRAINT msg_fk_notype FOREIGN KEY (notype_id) REFERENCES loco.notype;
ALTER TABLE loco.snapmsgreq
   ALTER COLUMN valuedate SET NOT NULL
  ,ALTER COLUMN notype_id SET NOT NULL
  ,ALTER COLUMN tot_req SET NOT NULL
  ,ALTER COLUMN tot_proc SET NOT NULL
  ,ALTER COLUMN tot_cancelled SET NOT NULL
  ,ALTER COLUMN tot_part_canc SET NOT NULL
  ,ALTER COLUMN tot_msgs SET NOT NULL
  ,ALTER COLUMN tot_msgs_sent SET NOT NULL
  ,ALTER COLUMN tot_msgs_failed SET NOT NULL
  ,ALTER COLUMN tot_msgs_retrys SET NOT NULL
;
ALTER TABLE loco.nores
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN filename SET NOT NULL
  ,ALTER COLUMN content SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.notemplcfg
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN notype_id SET NOT NULL
  ,ALTER COLUMN corrtype_id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN activate SET NOT NULL
  ,ALTER COLUMN templ SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.notemplcfg ADD CONSTRAINT notemplcfg_fk_notype FOREIGN KEY (notype_id) REFERENCES loco.notype;
ALTER TABLE loco.notemplcfg ADD CONSTRAINT notemplcfg_fk_corrtype FOREIGN KEY (corrtype_id) REFERENCES loco.corrtype;
ALTER TABLE loco.corrtypeallow
   ALTER COLUMN corrtype_id SET NOT NULL
  ,ALTER COLUMN allow_id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.corrtypeallow ADD CONSTRAINT corrtypeallow_fk_corrtype FOREIGN KEY (corrtype_id) REFERENCES loco.corrtype;
ALTER TABLE loco.config
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN value SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.nodict
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.snapprov
   ALTER COLUMN valuedate SET NOT NULL
  ,ALTER COLUMN corrtype_id SET NOT NULL
  ,ALTER COLUMN corrprov_id SET NOT NULL
  ,ALTER COLUMN msg_sent SET NOT NULL
  ,ALTER COLUMN msg_failed SET NOT NULL
  ,ALTER COLUMN msg_retry SET NOT NULL
  ,ALTER COLUMN avg_msgtime SET NOT NULL
  ,ALTER COLUMN tot_msgtime SET NOT NULL
;
ALTER TABLE loco.msgreq
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN priority SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN time_req SET NOT NULL
  ,ALTER COLUMN time_to_send SET NOT NULL
  ,ALTER COLUMN msg_addr SET NOT NULL
  ,ALTER COLUMN cust_res SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE loco.msgreq ADD CONSTRAINT msgreq_fk_notype FOREIGN KEY (notype_id) REFERENCES loco.notype;
CREATE INDEX corrprovcfg_ix_activate ON loco.corrprovcfg
(
   status
  ,activate
);
CREATE INDEX corrprovcfg_ix_deactive ON loco.corrprovcfg
(
   status
  ,deactivate
);
CREATE INDEX nodict_ix_keval ON loco.nodict
(
   id
  ,value
);
CREATE INDEX msgreqres_ix_msgreq ON loco.msgreqres
(
   msgreq_id
);
CREATE INDEX msgreq_ix_notype ON loco.msgreq
(
   notype_id
);
CREATE INDEX msgreq_ix_tosend ON loco.msgreq
(
   status
  ,time_to_send
);
CREATE INDEX msg_ix_mr ON loco.msg
(
   msgreq_id
);
CREATE INDEX msg_ix_mrs ON loco.msg
(
   msgreq_id
  ,status
);
CREATE INDEX msg_ix_proc ON loco.msg
(
   corrtype_id
  ,status
  ,priority
);
CREATE INDEX notemplcfg_ix_activate ON loco.notemplcfg
(
   status
  ,activate
);
CREATE INDEX notemplcfg_ix_deactive ON loco.notemplcfg
(
   status
  ,deactivate
);
INSERT INTO audit.cfg SELECT 'loco.config',       'id',                   'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.config');
INSERT INTO audit.cfg SELECT 'loco.corrprovcfg',  'id',                   'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.corrprovcfg');
INSERT INTO audit.cfg SELECT 'loco.corrtype',     'id',                   'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.corrtype');
INSERT INTO audit.cfg SELECT 'loco.corrtypeallow','corrtype_id|allow_id', 'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.corrtypeallow');
INSERT INTO audit.cfg SELECT 'loco.nodict',       'id',                   'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.nodict');
INSERT INTO audit.cfg SELECT 'loco.notemplcfg',   'id',                   'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.notemplcfg');
INSERT INTO audit.cfg SELECT 'loco.notype',       'id',                   'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'T' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'loco.notype');
INSERT INTO loco.config VALUES('msg.archive-age.sent',        'Max days before a sent message is archived',       '10',    'Archive', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.config VALUES('msg.archive-age.pending',     'Max days before a pending message is archived',    '365',   'Archive', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.config VALUES('msg.archive-age.failed',      'Max days before a failed message is archived',     '365',   'Archive', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.config VALUES('msg.archive-age.retry',       'Max days before a retry message is archived',      '365',   'Archive', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.config VALUES('msg.archive-age.cancelled',   'Max days before a cancelled message is archived',  '10',    'Archive', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.config VALUES('server.proc-interval',     'Server process interval (seconds)',          '1.0',      'Server', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.config VALUES('server.prov-interval',     'Server prover refresh interval (seconds)',   '3600.0',   'Server', '[loco]', CURRENT_TIMESTAMP);
INSERT INTO loco.corrtype SELECT 'email', 'E-Mail', 'A', '[{"id": "subject", "required": false, "descr": "Email Subject"}, {"id": "body-html", "required": false, "descr": "HTML Email Body"}, {"id":"body-text", "required": true, "descr": "Plain Text Email Body"}]', '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.corrtype SELECT 'sms',   'SMS',    'A', '[{"id":"msg", "required": true, "descr": "The sms message"}]', '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.corrprov SELECT 'logfile', 'email',  'Record Email to a log file',  'A', '[{"id": "path", "type": "string", "descr": "Path to the output log file."}]', '{"path": "$LOCAL_PATH/log/loco-email.log"}', NULL, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.corrprov SELECT 'logfile', 'sms',    'Record SMS to a log file',    'A', '[{"id": "path", "type": "string", "descr": "Path to the output log file."}]', '{"path": "$LOCAL_PATH/log/loco-sms.log"}',   NULL, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.corrprov SELECT 'awssns',  'sms',    'Send SMS via AWS Simple Notification Service',  'D', '[{"id": "aws_access_key_id", "type": "string", "descr": "AWS access key."}, {"id": "aws_secret_access_key", "type": "string", "descr": "AWS secret access key."}, {"id": "aws_region", "type": "string", "descr": "AWS region."}]', '{"aws_access_key_id": "$AWS_ACCESS_KEY_ID", "aws_secret_access_key": "$AWS_SECRET_ACCESS_KEY", "aws_region": "$AWS_REGION"}', NULL, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.corrprov SELECT 'smtp',    'email',  'Send Email via SMTP',  'D', '[{"id": "host", "type": "string", "descr": "Host name"}, {"id": "port", "type": "int", "descr": "Port number"}, {"id": "username", "type": "string", "descr": "Account user name"}, {"id": "passwd", "type": "string", "descr": "Account password"}, {"id": "from", "type": "string", "descr": "From email address"}, {"id": "ssl", "type": "boolean", "descr": "SSL Enabled"}, {"id": "tls", "type": "boolean", "descr": "TLS Enabled"}, {"id": "timeout", "type": "float", "descr": "Timeout"}]', '{"host": "$SMTP_HOST", "port": "$SMTP_PORT", "username": "$SMTP_USER" , "passwd": "$SMTP_PASSWD", "from": "loco@bitsmiths.co.za", "ssl": true, "tls": true, "timeout": 30.0}', NULL, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.corrprov SELECT 'bulksms', 'sms',    'Send SMS via Bulk SMS',  'D', '[{"id": "url", "type": "string", "descr": "Bulk SMS Endpoint URL."}, {"id": "username", "type": "string", "descr": "Bulk SMS user name."}, {"id": "passwd", "type": "string", "descr": "Bulkd SMS user password."}]', '{"url": "https://api.bulksms.com/v1/messages", "token": "$BULK_SMS_TOKEN", "token-secret": "$BULK_SMS_TOKEN_SECRET"}', NULL, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.notype  SELECT 'loco.test-msg', 'A',     'Bitsmiths LOCO Test message', 'Tests', 20, NULL, 0, 5, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.notempl SELECT 'loco.test-msg', 'email', 'A', NULL, '{"body-text": "Hello\nThis is a standard test plain text email from ${usrid}\nHave a nice day", "body-html": "<html><body><h3>Hello</h3><p>This is a standard HTML email from <b>${usrid}</b></p><p>Have a nice day</p></body></html>", "subject": "Loco Test Message"}', NULL, '[loco]', CURRENT_TIMESTAMP;
INSERT INTO loco.notempl SELECT 'loco.test-msg', 'sms',   'A', NULL, '{"msg": "Hello\nThis is a standard test sms from ${usrid}\nHave a nice day"}', NULL, '[loco]', CURRENT_TIMESTAMP;
