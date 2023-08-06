CREATE TABLE audit.aud (
   id SERIAL8
  ,tran_id BIGINT
  ,action character(1)
  ,tbl_id VARCHAR
  ,tbl_key VARCHAR
);
ALTER TABLE audit.aud ADD PRIMARY KEY (
   id
);
CREATE TABLE audit.cfg (
   id VARCHAR
  ,col_pk VARCHAR
  ,col_ignr VARCHAR
  ,par_id VARCHAR
  ,par_col VARCHAR
  ,last_chg TIMESTAMP
  ,audby_col VARCHAR
  ,MODE character(1)
);
ALTER TABLE audit.cfg ADD PRIMARY KEY (
   id
);
CREATE TABLE audit.tran (
   id SERIAL8
  ,site_id INTEGER
  ,who varchar(128)
  ,src varchar(128)
  ,tm_stamp TIMESTAMP
);
ALTER TABLE audit.tran ADD PRIMARY KEY (
   id
);
CREATE TABLE audit.col (
   aud_id BIGINT
  ,name VARCHAR
  ,BEFORE VARCHAR
  ,AFTER VARCHAR
);
ALTER TABLE audit.col ADD PRIMARY KEY (
   aud_id
  ,name
);
ALTER TABLE audit.tran
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN site_id SET NOT NULL
  ,ALTER COLUMN who SET NOT NULL
  ,ALTER COLUMN src SET NOT NULL
  ,ALTER COLUMN tm_stamp SET NOT NULL
;
ALTER TABLE audit.cfg
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN MODE SET NOT NULL
;
ALTER TABLE audit.cfg ADD CONSTRAINT cfg_fk_cfg FOREIGN KEY (par_id) REFERENCES audit.cfg;
ALTER TABLE audit.col
   ALTER COLUMN aud_id SET NOT NULL
  ,ALTER COLUMN name SET NOT NULL
;
ALTER TABLE audit.col ADD CONSTRAINT col_fk_aud FOREIGN KEY (aud_id) REFERENCES audit.aud;
ALTER TABLE audit.aud
   ALTER COLUMN id SET NOT NULL
  ,ALTER COLUMN tran_id SET NOT NULL
  ,ALTER COLUMN action SET NOT NULL
  ,ALTER COLUMN tbl_id SET NOT NULL
  ,ALTER COLUMN tbl_key SET NOT NULL
;
ALTER TABLE audit.aud ADD CONSTRAINT aud_fk_tran FOREIGN KEY (tran_id) REFERENCES audit.tran;
CREATE INDEX cfg_ix_par ON audit.cfg
(
   par_id
);
CREATE INDEX cfg_ix_lc ON audit.cfg
(
   id
  ,last_chg
);
CREATE INDEX aud_ix_tran ON audit.aud
(
   tran_id
);
CREATE INDEX col_uk_aud ON audit.col
(
   aud_id
);
CREATE OR REPLACE FUNCTION audit.audit_table_changes(cfg record, tran_id bigint, action text, new_rec JSONB, old_rec JSONB)
  RETURNS void
  VOLATILE
  SECURITY DEFINER
  LANGUAGE PLPGSQL
AS $$
declare
  aud_id bigint;
  pkey_cols text[] = STRING_TO_ARRAY(cfg.col_pk, '|');
  ignor_cols text[] = STRING_TO_ARRAY(cfg.col_ignr, '|');
  pcol text = null;
  aud_pk text = null;
  pk_txt text = null;
  _key text;
  _value text;
begin
  foreach pcol in array pkey_cols
  loop
    if (action = 'D') then
      pk_txt := (old_rec->>pcol)::text;
    else
      pk_txt := (new_rec->>pcol)::text;
    end if;

    if aud_pk is null then
      aud_pk := pk_txt;
    else
      aud_pk := format('%s|%s', aud_pk, pk_txt);
    end if;
  end loop;

  insert into audit.aud select nextval('audit.aud_id_seq'), tran_id, action, cfg.id, aud_txt;

  aud_id := currval('audit.aud_id_seq');

  if (action = 'D') then
    for _key, _value in select * from jsonb_each_text(old_rec)
    loop
      insert into audit.col select aud_id, _key, _value, null where not _key = any(ignor_cols);
    end loop;
  elseif (action = 'U') then
    for _key, _value in select * from jsonb_each_text(new_rec)
    loop
      insert into audit.col
        select aud_id, _key, (old_rec->>_key)::text, _value
          where not _key = any(ignor_cols) and _value != (old_rec->>_key)::text;
    end loop;
  else
    for _key, _value in select * from jsonb_each_text(new_rec)
    loop
      insert into audit.col select aud_id, _key, null, _value::text where not _key = any(ignor_cols);
    end loop;
  end if;
end;
$$;
CREATE OR REPLACE FUNCTION audit.audit_stamp_table(TABLE_NAME text, SCHEMA_NAME text = 'public')
  RETURNS void
  VOLATILE
  SECURITY DEFINER
  LANGUAGE PLPGSQL
AS $$
declare
  cfg record;
  tran_id bigint;
  cfg_id text := table_name;
  rec record;
begin
  if (schema_name != 'public') then
    cfg_id := format('%s.%s', schema_name, table_name);
  end if;

  select c.* into cfg from audit.cfg c where c.id = cfg_id;

  insert into audit.tran select nextval('audit.tran_id_seq'), 0, '[STAMPED]', '[audit.trigger]', current_timestamp;

  tran_id := currval('audit.tran_id_seq');

  for rec in execute 'select * from ' || cfg_id
  loop
    perform audit.audit_table_changes(cfg, tran_id, 'S', to_jsonb(rec), null);
  end loop;
end;
$$;
CREATE OR REPLACE FUNCTION audit.insert_update_delete_trigger()
  RETURNS TRIGGER
  VOLATILE
  SECURITY DEFINER
  LANGUAGE PLPGSQL
AS $$
declare
  tran_id bigint;
  cfg record;
  cfg_id text = TG_TABLE_NAME;
  action text;
  stamp_by text;
  pkey_cols text[];
  new_rec jsonb;
  old_rec jsonb;
begin
  if TG_TABLE_SCHEMA != 'public' then
    cfg_id := format('%s.%s', TG_TABLE_SCHEMA, TG_TABLE_NAME);
  end if;

  select c.* into cfg from audit.cfg c where c.id = cfg_id;
  stamp_by := coalesce(new_rec->>cfg.audby_col, '[???]');

  insert into audit.tran select nextval('audit.tran_id_seq'), 0, stamp_by, '[audit.trigger]', current_timestamp;

  tran_id := currval('audit.tran_id_seq');

  if (TG_OP = 'INSERT') then
    action := 'C';
    new_rec := to_jsonb(new);
  elseif (TG_OP = 'UPDATE') then
    action := 'U';
    new_rec := to_jsonb(new);
    old_rec := to_jsonb(old);
  elseif (TG_OP = 'DELETE') then
    action := 'D';
    old_rec := to_jsonb(old);
  end if;

  perform audit.audit_table_changes(cfg, tran_id, action, new_rec, old_rec);

  update audit.cfg set last_chg = current_timestamp where id = cfg_id;

  return coalesce(new, old);
end;
$$;
CREATE OR REPLACE FUNCTION audit.enable_tracking(regclass)
  RETURNS void
  VOLATILE
  SECURITY DEFINER
  LANGUAGE PLPGSQL
AS $$
declare
  statement_row text = format('
    create trigger
      audit_i_u_d
    after
      insert or update or delete on %s
    for each row
      execute procedure audit.insert_update_delete_trigger();', $1
  );
begin
    if not exists(select 1 from pg_trigger where tgrelid = $1 and tgname = 'audit_i_u_d') then
      execute statement_row;
    end if;
end;
$$;
CREATE OR REPLACE FUNCTION audit.disable_tracking(regclass)
  RETURNS void
  VOLATILE
  SECURITY DEFINER
  LANGUAGE PLPGSQL
AS $$
declare
  statement_row text = format('drop trigger if exists audit_i_u_d on %s;', $1);
begin
  execute statement_row;
end;
$$;
CREATE OR REPLACE FUNCTION audit.refresh_tracking()
  RETURNS void
  VOLATILE
  SECURITY DEFINER
  LANGUAGE PLPGSQL
AS $$
declare
  rec record;
begin
  for rec in select * from audit.cfg
  loop
    if (rec.mode = 'T') then
      perform audit.enable_tracking(rec.id);
    else
      perform audit.disable_tracking(rec.id);
    end if;
  end loop;
end;
$$;
CREATE OR REPLACE FUNCTION audit.show_trail(
  arg_tbl_id text[],
  arg_pk_ids text[] = NULL,
  arg_col_ids text[] = NULL,
  arg_date_from TIMESTAMP= NULL,
  arg_date_to TIMESTAMP = NULL,
  arg_actions text[] = NULL
  )
  RETURNS TABLE (
    "TRAN" bigint,
    "Stamp" TIMESTAMP,
    "Who" text,
    "AUD" bigint,
    "Action" text,
    "Table" text,
    "Key" text,
    "Column" text,
    "Before" text,
    "After" text
  )
  VOLATILE
  SECURITY DEFINER
  LANGUAGE SQL
AS $func$
select
  tran.id,
  tran.tm_stamp,
  tran.who,
  aud.id,
  case
    when aud.action = 'C' then 'Created'
    when aud.action = 'U' then 'Updated'
    when aud.action = 'D' then 'Deleted'
    when aud.action = 'S' then 'Stamped'
    else '???'
  end,
  aud.tbl_id,
  aud.tbl_key,
  col.name,
  col.before,
  col.after
from
  audit.tran tran
    join
  audit.aud aud
    on aud.tran_id = tran.id
    join
  audit.col col
    on col.aud_id = aud.id
where
  aud.tbl_id = any(arg_tbl_id) and
  (arg_pk_ids is null or aud.tbl_key = any(arg_pk_ids)) and
  (arg_col_ids is null or col.name = any(arg_col_ids)) and
  (arg_date_from is null or tran.tm_stamp >= arg_date_from) and
  (arg_date_to is null or tran.tm_stamp <= arg_date_to) and
  (arg_actions is null or aud.action = any(arg_actions))
order by
  tran.tm_stamp desc,
  aud.id desc
;
$func$;
