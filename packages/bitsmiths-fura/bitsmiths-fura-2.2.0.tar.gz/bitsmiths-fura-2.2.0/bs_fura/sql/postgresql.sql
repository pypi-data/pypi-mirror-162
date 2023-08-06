CREATE TABLE fura.sitecfg (
   site_id INTEGER
  ,id varchar(256)
  ,descr varchar(256)
  ,value varchar(4096)
  ,modified_by varchar(64)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.sitecfg ADD PRIMARY KEY (
   site_id
  ,id
);
CREATE TABLE fura.funcgrp (
   id varchar(128)
  ,descr varchar(256)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.funcgrp ADD PRIMARY KEY (
   id
);
CREATE TABLE fura.eatok (
   id SERIAL8
  ,tok varchar(256)
  ,site_id INTEGER
  ,usr_id varchar(128)
  ,func_id varchar(128)
  ,grant_usr_id varchar(128)
  ,created TIMESTAMP
  ,expires TIMESTAMP
  ,max_usages INTEGER
  ,usages INTEGER
);
ALTER TABLE fura.eatok ADD PRIMARY KEY (
   id
);
CREATE TABLE fura.token (
   site_id INTEGER
  ,id varchar(64)
  ,usr_id varchar(128)
  ,date_created TIMESTAMP
  ,expires TIMESTAMP
  ,use_cnt INTEGER
  ,audid VARCHAR
  ,tmstamp TIMESTAMP
);
ALTER TABLE fura.token ADD PRIMARY KEY (
   site_id
  ,id
);
CREATE TABLE fura.rolefuncrel (
   site_id INTEGER
  ,role_id varchar(128)
  ,func_id varchar(128)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.rolefuncrel ADD PRIMARY KEY (
   site_id
  ,role_id
  ,func_id
);
CREATE TABLE fura.ula (
   site_id INTEGER
  ,site_code varchar(32)
  ,tm_stamp TIMESTAMP
  ,usr_id varchar(128)
  ,err_code INTEGER
  ,state character(1)
  ,action character(1)
  ,auth_type character(1)
  ,auth_ip varchar(32)
  ,auth_geo varchar(64)
);
CREATE TABLE fura.tokensentry (
   site_id INTEGER
  ,token_cnt BIGINT
  ,last_poll TIMESTAMP
);
ALTER TABLE fura.tokensentry ADD PRIMARY KEY (
   site_id
);
CREATE TABLE fura.role (
   site_id INTEGER
  ,id varchar(128)
  ,descr varchar(256)
  ,status character(1)
  ,LEVEL INTEGER
  ,sess_timeout INTEGER
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.role ADD PRIMARY KEY (
   site_id
  ,id
);
CREATE TABLE fura.aga (
   site_id INTEGER
  ,site_code varchar(32)
  ,tm_stamp TIMESTAMP
  ,usr_id varchar(128)
  ,eausr_id varchar(128)
  ,role_id varchar(128)
  ,func_id varchar(128)
  ,action character(1)
  ,src varchar(128)
);
CREATE TABLE fura.usr (
   site_id INTEGER
  ,id varchar(128)
  ,role_id varchar(128)
  ,status character(1)
  ,name_first varchar(128)
  ,name_last varchar(128)
  ,title varchar(5)
  ,date_activate DATE
  ,date_expire DATE
  ,email1 varchar(256)
  ,email2 varchar(256)
  ,cellno1 varchar(32)
  ,cellno2 varchar(32)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
  ,usrtype_id varchar(32)
  ,email1_conf BOOLEAN
  ,email2_conf BOOLEAN
  ,cellno1_conf BOOLEAN
  ,cellno2_conf BOOLEAN
  ,opt_system BOOLEAN
  ,opt_market BOOLEAN
  ,opt_fail_login BOOLEAN
);
ALTER TABLE fura.usr ADD PRIMARY KEY (
   site_id
  ,id
);
CREATE TABLE fura.usrotp (
   site_id INTEGER
  ,usr_id varchar(128)
  ,otp_method character(1)
  ,otp varchar(128)
  ,expire TIMESTAMP
  ,used BOOLEAN
  ,target varchar(64)
  ,fail_cnt INTEGER
  ,meta_data JSONB
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.usrotp ADD PRIMARY KEY (
   site_id
  ,usr_id
);
CREATE TABLE fura.ada (
   site_id INTEGER
  ,site_code varchar(32)
  ,tm_stamp TIMESTAMP
  ,usr_id varchar(128)
  ,eausr_id varchar(128)
  ,role_id varchar(128)
  ,func_id varchar(128)
  ,action character(1)
  ,src varchar(128)
  ,reason varchar(128)
);
CREATE TABLE fura.config (
   id varchar(256)
  ,descr varchar(256)
  ,value varchar(4096)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.config ADD PRIMARY KEY (
   id
);
CREATE TABLE fura.site (
   id serial4
  ,code varchar(32)
  ,descr varchar(256)
  ,status character(1)
  ,cc varchar(2)
  ,ccy varchar(3)
  ,dc varchar(3)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.site ADD PRIMARY KEY (
   id
);
CREATE TABLE fura.usrauth (
   site_id INTEGER
  ,usr_id varchar(128)
  ,auth_type character(1)
  ,auth_data varchar(4096)
  ,fail_cnt INTEGER
  ,salt varchar(128)
  ,last_ip varchar(32)
  ,last_geo varchar(64)
  ,last_succ TIMESTAMP
  ,last_fail TIMESTAMP
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.usrauth ADD PRIMARY KEY (
   site_id
  ,usr_id
  ,auth_type
);
CREATE TABLE fura.func (
   id varchar(128)
  ,funcgrp_id varchar(128)
  ,descr varchar(256)
  ,action character(1)
  ,oride character(1)
  ,audit_lvl INTEGER
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.func ADD PRIMARY KEY (
   id
);
CREATE TABLE fura.tokenhist (
   site_id INTEGER
  ,id varchar(64)
  ,usr_id varchar(128)
  ,date_created TIMESTAMP
  ,expires TIMESTAMP
  ,use_cnt INTEGER
  ,audid VARCHAR
  ,tmstamp TIMESTAMP
);
CREATE TABLE fura.usrtype (
   id varchar(32)
  ,descr varchar(128)
  ,modified_by varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE fura.usrtype ADD PRIMARY KEY (
   id
);
ALTER TABLE fura.tokensentry
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN token_cnt SET NOT NULL
  ,ALTER COLUMN last_poll SET NOT NULL
;
ALTER TABLE fura.tokensentry ADD CONSTRAINT tokensentry_fk_site FOREIGN KEY (site_id) REFERENCES fura.site;
ALTER TABLE fura.token
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN date_created SET NOT NULL
  ,ALTER COLUMN expires SET NOT NULL
  ,ALTER COLUMN use_cnt SET NOT NULL
  ,ALTER COLUMN audid SET NOT NULL
  ,ALTER COLUMN tmstamp SET NOT NULL
;
ALTER TABLE fura.token ADD CONSTRAINT token_fk_site FOREIGN KEY (site_id) REFERENCES fura.site;
ALTER TABLE fura.token ADD CONSTRAINT token_fk_usr FOREIGN KEY (site_id, usr_id) REFERENCES fura.usr;
ALTER TABLE fura.usrauth
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN auth_type SET NOT NULL
  ,ALTER COLUMN fail_cnt SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.usrauth ADD CONSTRAINT usrauth_fk_usr FOREIGN KEY (site_id, usr_id) REFERENCES fura.usr;
ALTER TABLE fura.ula
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
  ,ALTER COLUMN err_code SET NOT NULL
  ,ALTER COLUMN state SET NOT NULL
  ,ALTER COLUMN action SET NOT NULL
  ,ALTER COLUMN auth_type SET NOT NULL
;
ALTER TABLE fura.tokenhist
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN date_created SET NOT NULL
  ,ALTER COLUMN expires SET NOT NULL
  ,ALTER COLUMN use_cnt SET NOT NULL
  ,ALTER COLUMN audid SET NOT NULL
  ,ALTER COLUMN tmstamp SET NOT NULL
;
ALTER TABLE fura.aga
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN site_code SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN role_id SET NOT NULL
  ,ALTER COLUMN func_id SET NOT NULL
  ,ALTER COLUMN action SET NOT NULL
;
ALTER TABLE fura.role
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN LEVEL SET NOT NULL
  ,ALTER COLUMN sess_timeout SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.role ADD CONSTRAINT role_fk_site FOREIGN KEY (site_id) REFERENCES fura.site;
ALTER TABLE fura.usr
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
  ,ALTER COLUMN usrtype_id SET NOT NULL
  ,ALTER COLUMN email1_conf SET NOT NULL
  ,ALTER COLUMN email2_conf SET NOT NULL
  ,ALTER COLUMN cellno1_conf SET NOT NULL
  ,ALTER COLUMN cellno2_conf SET NOT NULL
  ,ALTER COLUMN opt_system SET NOT NULL
  ,ALTER COLUMN opt_market SET NOT NULL
  ,ALTER COLUMN opt_fail_login SET NOT NULL
;
ALTER TABLE fura.usr ADD CONSTRAINT usr_fk_site FOREIGN KEY (site_id) REFERENCES fura.site;
ALTER TABLE fura.usr ADD CONSTRAINT usr_fk_usrtype FOREIGN KEY (usrtype_id) REFERENCES fura.usrtype;
ALTER TABLE fura.usr ADD CONSTRAINT usr_fk_role FOREIGN KEY (site_id, role_id) REFERENCES fura.role;
ALTER TABLE fura.rolefuncrel
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN role_id SET NOT NULL
  ,ALTER COLUMN func_id SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.sitecfg
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.usrtype
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.funcgrp
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.ada
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN site_code SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN role_id SET NOT NULL
  ,ALTER COLUMN func_id SET NOT NULL
  ,ALTER COLUMN action SET NOT NULL
  ,ALTER COLUMN reason SET NOT NULL
;
ALTER TABLE fura.config
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.usrotp
   ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN otp_method SET NOT NULL
  ,ALTER COLUMN used SET NOT NULL
  ,ALTER COLUMN fail_cnt SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.usrotp ADD CONSTRAINT usrotp_fk_usr FOREIGN KEY (site_id, usr_id) REFERENCES fura.usr;
ALTER TABLE fura.eatok
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN tok SET NOT NULL
  ,ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN usr_id SET NOT NULL
  ,ALTER COLUMN func_id SET NOT NULL
  ,ALTER COLUMN grant_usr_id SET NOT NULL
  ,ALTER COLUMN created SET NOT NULL
  ,ALTER COLUMN expires SET NOT NULL
  ,ALTER COLUMN max_usages SET NOT NULL
  ,ALTER COLUMN usages SET NOT NULL
;
ALTER TABLE fura.eatok ADD CONSTRAINT eatok_fk_usr FOREIGN KEY (site_id, usr_id) REFERENCES fura.usr;
ALTER TABLE fura.eatok ADD CONSTRAINT eatok_fk_grant FOREIGN KEY (site_id, grant_usr_id) REFERENCES fura.usr;
ALTER TABLE fura.eatok ADD CONSTRAINT eatok_fk_func FOREIGN KEY (func_id) REFERENCES fura.func;
ALTER TABLE fura.eatok ADD CONSTRAINT eatok_uk_tok UNIQUE (
   tok
  ,site_id
);
ALTER TABLE fura.site
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN status SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.site ADD CONSTRAINT site_uk_code UNIQUE (
   code
);
ALTER TABLE fura.func
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN funcgrp_id SET NOT NULL
  ,ALTER COLUMN descr SET NOT NULL
  ,ALTER COLUMN action SET NOT NULL
  ,ALTER COLUMN oride SET NOT NULL
  ,ALTER COLUMN audit_lvl SET NOT NULL
  ,ALTER COLUMN modified_by SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE fura.func ADD CONSTRAINT func_fk_funcgrp FOREIGN KEY (funcgrp_id) REFERENCES fura.funcgrp;
CREATE INDEX usrauth_ix_token ON fura.usrauth
(
   site_id
  ,auth_type
  ,auth_data
);
CREATE INDEX usr_ix_role ON fura.usr
(
   site_id
  ,role_id
);
CREATE INDEX usr_ix_usrtype ON fura.usr
(
   site_id
  ,usrtype_id
);
CREATE INDEX func_ix_funcgrp ON fura.func
(
   funcgrp_id
);
INSERT INTO audit.cfg SELECT 'fura.config',        'id',                       'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.config');
INSERT INTO audit.cfg SELECT 'fura.func',          'id',                       'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.func');
INSERT INTO audit.cfg SELECT 'fura.site',          'id',                       'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.site');
INSERT INTO audit.cfg SELECT 'fura.sitecfg',       'site_id|id',               'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.sitecfg');
INSERT INTO audit.cfg SELECT 'fura.role',          'site_id|id',               'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.role');
INSERT INTO audit.cfg SELECT 'fura.rolefuncrel',   'site_id|role_id|func_id',  'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.rolefuncrel');
INSERT INTO audit.cfg SELECT 'fura.usr',           'site_id|id',               'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.usr');
INSERT INTO audit.cfg SELECT 'fura.usrtype',       'id',                       'modified_by|tm_stamp', NULL, NULL, NULL, 'modified_by', 'M' WHERE NOT EXISTS (SELECT id FROM audit.cfg WHERE id = 'fura.usrtype');
INSERT INTO fura.funcgrp VALUES('FURA-ADMIN', 'Fura Administration', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.funcgrp VALUES('FURA',       'Fura',                '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.cfg.create',    'FURA-ADMIN', 'Create a config',   'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.cfg.read',      'FURA-ADMIN', 'Read a config',     'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.cfg.update',    'FURA-ADMIN', 'Update a config',   'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.cfg.delete',    'FURA-ADMIN', 'Delete a config',   'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.site.create',   'FURA-ADMIN', 'Create a site',   'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.site.read',     'FURA-ADMIN', 'Read a site',     'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.site.update',   'FURA-ADMIN', 'Update a site',   'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.site.delete',   'FURA-ADMIN', 'Delete a site',   'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usrtype.create',   'FURA-ADMIN', 'Create a user type',   'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usrtype.read',     'FURA-ADMIN', 'Read a user type',     'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usrtype.update',   'FURA-ADMIN', 'Update a user type',   'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usrtype.delete',   'FURA-ADMIN', 'Delete a user type',   'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.site VALUES(1, 'FURA', 'Fura Administration', 'A', 'ZA', 'ZAR', '27', '[fura]', CURRENT_TIMESTAMP);
SELECT setval('fura.site_id_seq', 1);
INSERT INTO fura.config VALUES ('audit.denied.level',  'Audit Denied Level',              '100', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('audit.denied.age',    'Audit Denied Max Age (days)',     '90',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('audit.granted.level', 'Audit Granted Level',             '100', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('audit.granted.age',   'Audit Granted Max Age (days)',    '90',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('audit.usrlogin.age',  'Audit User Login Max Age (days)', '90',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('paths.salt',        'Salt directory', 'env/fura/salt',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('token.webkey',      'Web token key',  '{"k":"ADkGzwL3kKBljqhH-7OR7ZQeSLMx5rmihwuPVWfgjeM","kty":"oct"}', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('otp.sms.length',    'Length of SMS One Time Pins.', '6', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('otp.sms.content',   'Content of SMS OTP, [alpha, numeric, or alphanumeric]', 'numeric', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('otp.sms.timeout',   'Time-out for SMS OTPs in minutes',   '5',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('otp.email.length',  'Length of e-mail OTP.', '6', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('otp.email.content', 'Content of e-mail OTP, [alpha, numeric, or alphanumeric]', 'alphanumeric', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('otp.email.timeout', 'Time-out for auth reset emails in minutes', '10', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('loco.trigger.type', 'The Loco trigger interface to use.', 'local_db', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('loco.trigger.cfg',  'The Loco trigger config.', '{"dao" : "postgresql"}', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('authreset.urlmask.email', 'The URL mask to email the user.  Use $site, $usr, $tok, and $authtype for replacement.', 'http://fura_example.co.za/resetUserAuth?site=$site&usr=$usr&otp=$otp&authtype=$authtype&otpmethod=$otpmethod', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('authreset.urlmask.sms',   'The URL mask to sms the user.  Use $site, $usr, $otp, and $authtype for replacement.',   'http://fura_example.co.za/resetUserAuth?site=$site&usr=$usr&otp=$otp&authtype=$authtype&otpmethod=$otpmethod', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('authreset.support-email', 'The support email address to use for auth resets.', 'support@bitsmiths.co.za', '[FURA]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('loco.authreset',          'Reset account loco type to use.',        'fura.reset_passwd',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('loco.usrreg',             'New registration loco type to use.',     'fura.registration',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('loco.login_attempt',      'Failed login attempt loco type to use.', 'fura.login_attempt', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('loco.confirm_addr',       'Confirm address loco type to use.',      'fura.confirm_addr',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('auth-policy.P.descr', 'Auth password policy description.', 'Minimum ten characters, at least one uppercase letter, one lowercase letter, one number and one special character.', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.config VALUES ('auth-policy.P.regex', 'Auth passowrd policy regex.',       '^(?=.*?[A-Z])(?=(.*[a-z]){1,})(?=(.*[\d]){1,})(?=(.*[\W]){1,})(?!.*\s).{10,}$', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.sitecfg VALUES (1, 'audit.denied.level',  'Audit Denied Level',              '100', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.sitecfg VALUES (1, 'audit.denied.age',    'Audit Denied Max Age (days)',     '90',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.sitecfg VALUES (1, 'audit.granted.level', 'Audit Granted Level',             '100', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.sitecfg VALUES (1, 'audit.granted.age',   'Audit Granted Max Age (days)',    '90',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.sitecfg VALUES (1, 'audit.usrlogin.age',  'Audit User Login Max Age (days)', '90',  '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.role VALUES (1, 'admin', 'Fura super user admin', 'S', 1, 60, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.usrtype VALUES ('sys',    'System User', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.usrtype VALUES ('client', 'Client User', '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.usr VALUES (
  1, 'admin', 'admin', 'A', 'Admin', 'Admin', NULL, CURRENT_DATE, NULL,
  'nicolas@bitsmiths.co.za', 'steven@bitsmiths.co.za', NULL, NULL, '[fura]', CURRENT_TIMESTAMP, 'sys',
  TRUE, TRUE, FALSE, FALSE, TRUE, TRUE, TRUE);
INSERT INTO fura.func VALUES('fura.role.create',   'FURA', 'Create a role',        'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.role.read',     'FURA', 'Read a role',          'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.role.update',   'FURA', 'Update a role',        'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.role.delete',   'FURA', 'Delete a role',        'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.rfr.add',       'FURA', 'Assign function to role',   'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.rfr.read',      'FURA', 'Read a role function',      'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.rfr.rem',       'FURA', 'Remove function from role', 'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.func.read',     'FURA', 'Read a function',        'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.funcgrp.read',  'FURA', 'Read a function group',  'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.service.create',  'FURA', 'Create a service matrix',    'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.service.read',    'FURA', 'Read a service matrix',      'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.service.update',  'FURA', 'Update a service matrix',    'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.service.delete',  'FURA', 'Delete a service matrix',    'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.create',      'FURA', 'Create a user',     'C', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.read',        'FURA', 'Read a user',       'R', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.update',      'FURA', 'Update a user',     'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.delete',      'FURA', 'Delete a user',     'D', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.activate',    'FURA', 'Activate a user',   'A', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.susp',        'FURA', 'Suspend a user',    'A', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.disable',     'FURA', 'Disable a user',    'A', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.reset-auth',  'FURA', 'Request a reset link (email) for a user.', 'O', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.reset-token', 'FURA', 'Request a token auth is reset (regenerated).', 'O', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.read-token',  'FURA', 'Read an auth token.', 'O', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO fura.func VALUES('fura.usr.setrole',     'FURA', 'Set a users role.', 'U', 'Y', 5, '[fura]', CURRENT_TIMESTAMP);
INSERT INTO loco.notype  SELECT 'fura.reset_passwd',       'A', 'Fura reset password',             'Fura', 10, NULL,       1,  5, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT id FROM loco.notype WHERE id = 'fura.reset_passwd');
INSERT INTO loco.notype  SELECT 'fura.registration',       'A', 'Fura new registration',           'Fura', 10, NULL,       1, 60, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT id FROM loco.notype WHERE id = 'fura.registration');
INSERT INTO loco.notype  SELECT 'fura.confirm_addr',       'A', 'Fura confirm email/sms address',  'Fura', 10, NULL,       1, 60, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT id FROM loco.notype WHERE id = 'fura.confirm_addr');
INSERT INTO loco.notype  SELECT 'fura.login_attempt',      'A', 'Fura failed login attempt',       'Fura', 10, '["sms"]',  1, 60, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT id FROM loco.notype WHERE id = 'fura.login_attempt');
INSERT INTO loco.notempl SELECT 'fura.reset_passwd',   'sms',   'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'sms'   AND notype_id = 'fura.reset_passwd');
INSERT INTO loco.notempl SELECT 'fura.reset_passwd',   'email', 'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'email' AND notype_id = 'fura.reset_passwd');
INSERT INTO loco.notempl SELECT 'fura.confirm_addr',   'sms',   'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'sms'   AND notype_id = 'fura.confirm_addr');
INSERT INTO loco.notempl SELECT 'fura.confirm_addr',   'email', 'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'email' AND notype_id = 'fura.confirm_addr');
INSERT INTO loco.notempl SELECT 'fura.login_attempt',  'sms',   'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'sms'   AND notype_id = 'fura.login_attempt');
INSERT INTO loco.notempl SELECT 'fura.login_attempt',  'email', 'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'email' AND notype_id = 'fura.login_attempt');
INSERT INTO loco.notempl SELECT 'fura.registration',   'sms',   'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'sms'   AND notype_id = 'fura.registration');
INSERT INTO loco.notempl SELECT 'fura.registration',   'email', 'A', NULL, '{}', NULL, '[fura]', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT notype_id FROM loco.notempl WHERE corrtype_id = 'email' AND notype_id = 'fura.registration');
UPDATE loco.notempl SET templ = '{}', modified_by = '[orv]', tm_stamp = CURRENT_TIMESTAMP WHERE notype_id like 'fura.%';
UPDATE loco.notempl
SET templ = '{"msg": "You are about to reset your ${site_descr}, OTP: ${otp}"}'
WHERE corrtype_id = 'sms' AND notype_id = 'fura.reset_passwd';
UPDATE loco.notempl
SET templ = '{"subject": "${site_descr} Password Reset", "body-text": "${site_descr}\n\nReset Password OTP: ${otp}\n\nDidn`t request a new password? If you need any help don`t hesitate to contact us at: ${support_email}", "body-html": "<!DOCTYPE html><html><head><title>Password Reset</title><style type=''text/css''> body { font-size: 0.87em; color: #ffffff; text-align: center; height: 100%;} h1  {font-size: 2.1em;} a {color: inherit;} img { display:block; width:100%; margin:-8% 0;}.img-row { overflow:hidden; margin:0;}.wrapper-div { margin: auto; max-width:600px;background-color: #373535ff;}.body-text {padding-top: 7%;}.body-text, .new-password-div {font-size: 1.2em;}.new-password-div { margin: auto; background-color: #90c84bff; padding: 2%; max-width: 35%; margin-top: 5%; font-weight: bold; color: #000000;}.footer-div { padding-top: 0.2%; padding-bottom: 2%; max-height: 7.857em; margin-top: 10%; background-color: #373535ff;}.footer-div, .body-text { padding-left: 10%; padding-right: 10%;}</style></head><body><div class=''wrapper-div''><div class=''row''><div class=''body-text''><h1>${site_descr}</h1><p><h3>Reset Password OTP : </h3><h2>${otp}</h2></p><p>Or to reset to your account in one easy step click the button below.</p></div><a style=''text-decoration:none'' href=''${httplink}''><div class=''new-password-div''>Reset My Password</div></a></div><div class=''row''><div class=''footer-div''><p>Didn`t request a new password?  If you need any help don`t hesitate to <a href=''mailto:${support_email}?subject=Mail from Our Site''>contact us.</a></p></div></div></div></body></html>" }'
WHERE corrtype_id = 'email' AND notype_id = 'fura.reset_passwd';
UPDATE loco.notempl
SET templ = '{"msg": "Failed login attempt for ${site_descr} detected on ${datetime}, remaining attempts: ${remaining}"}'
WHERE corrtype_id = 'sms' AND notype_id = 'fura.login_attempt';
UPDATE loco.notempl
SET templ = '{"subject": "Failed Login Attemp", "body-text": "${site_descr}\n\nFailed login attempt detected on ${datetime}, remaining attempts: ${remaining}\n\nDidn`t try an login? If you need any help don`t hesitate to contact us at: ${support_email}", "body-html": "<!DOCTYPE html><html><head><title>Failed Login Attempt</title><style type=''text/css''> body { font-size: 0.87em; color: #ffffff; text-align: center; height: 100%;} h1  {font-size: 2.1em;} a {color: inherit;} img { display:block; width:100%; margin:-8% 0;}.img-row { overflow:hidden; margin:0;}.wrapper-div { margin: auto; max-width:600px;background-color: #373535ff;}.body-text {padding-top: 7%; font-size: 1.0em}.body-text, .body-text { padding-left: 10%; padding-right: 10%;}</style></head><body><div class=''wrapper-div''><div class=''row''><div class=''body-text''><h1>${site_descr}</h1><p><h3>Failed Login Attempt!</h3></p><p>Failed login attempt detected on ${datetime}, remaining attempts: ${remaining}</p><p>Didn`t attempt to login?  If you need any help don`t hesitate to <a href=''mailto:${support_email}?subject=Mail from Our Site''>contact us.</a></p><br></div></div></div></div></body></html>" }'
WHERE corrtype_id = 'email' AND notype_id = 'fura.login_attempt';
UPDATE loco.notempl
SET templ = '{"msg": "You are about to confirm your ${site_descr} cell number, OTP: ${otp}"}'
WHERE corrtype_id = 'sms' AND notype_id = 'fura.confirm_addr';
UPDATE loco.notempl
SET templ = '{"subject": "Confirm You E-mail Address", "body-text": "${site_descr}\n\nConfirm OTP: ${otp}\n", "body-html": "<!DOCTYPE html><html><head><title>Confirm E-mail Address</title><style type=''text/css''> body { font-size: 0.87em; color: #ffffff; text-align: center; height: 100%;} h1 {font-size: 2.1em;} a {color: inherit;} img { display:block; width:100%; margin:-8% 0;}.img-row { overflow:hidden; margin:0;}.wrapper-div { margin: auto; max-width:600px;background-color: #373535ff;}.body-text {padding-top: 7%;}.body-text, .body-text { padding-left: 10%; padding-right: 10%;}</style></head><body><div class=''wrapper-div''><div class=''img-row''><img src=''mail-hero.png''></div><div class=''row''><div class=''body-text''><h1>${site_descr}</h1><p><h3>Confirm Your E-mail Address OTP : </h3><h2>${otp}</h2></p><p>If you need any help don`t hesitate to <a href=''mailto:${support_email}?subject=Mail from Our Site''>contact us.</a></p><br></div></div></div></div></div></body></html>" }'
WHERE corrtype_id = 'email' AND notype_id = 'fura.confirm_addr';
UPDATE loco.notempl
SET templ = '{"msg": "Your are about to complete your account registration with ${site_descr}, OTP: ${otp}"}'
WHERE corrtype_id = 'sms' AND notype_id = 'fura.registration';
UPDATE loco.notempl
SET templ = '{"subject": "${site_descr} Account Registration", "body-text": "${site_descr}\n\nAccount Registration OTP: ${otp}\n\nDidn`t register with us. No problem you can safely ignore this email or don`t hesitate to contact us at: ${support_email}", "body-html": "<!DOCTYPE html><html><head><title>Account Registration</title><style type=''text/css''> body { font-size: 0.87em; color: #ffffff; text-align: center; height: 100%;} h1  {font-size: 2.1em;} a {color: inherit;} img { display:block; width:100%; margin:-8% 0;}.img-row { overflow:hidden; margin:0;}.wrapper-div { margin: auto; max-width:600px;background-color: #373535ff;}.body-text {padding-top: 7%;}.body-text, .new-password-div {font-size: 1.2em;}.new-password-div { margin: auto; background-color: #90c84bff; padding: 2%; max-width: 35%; margin-top: 5%; font-weight: bold; color: #000000;}.footer-div { padding-top: 0.2%; padding-bottom: 2%; max-height: 7.857em; margin-top: 10%; background-color: #373535ff;}.footer-div, .body-text { padding-left: 10%; padding-right: 10%;}</style></head><body><div class=''wrapper-div''><div class=''row''><div class=''body-text''><h1>${site_descr}</h1><p><h3>Account Registration OTP : </h3><h2>${otp}</h2></p><p>Or to register to your account in one easy step click the button below.</p></div><a style=''text-decoration:none'' href=''${httplink}''><div class=''new-password-div''>Register My Account</div></a></div><div class=''row''><div class=''footer-div''><p>Didn`t register an account with us?  No problem, you can ignore this email or don`t hesitate to <a href=''mailto:${support_email}?subject=Mail from Our Site''>contact us.</a></p></div></div></div></body></html>" }'
WHERE corrtype_id = 'email' AND notype_id = 'fura.registration';
