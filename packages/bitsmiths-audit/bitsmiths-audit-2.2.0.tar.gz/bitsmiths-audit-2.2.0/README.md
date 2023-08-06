# BITSMITHS AUDIT #

This is the second tier base/core Bitsmiths python library. The purpose of this product is provide field level row
auditing for any tables or objects within a product.

This auditing product is used by our own open-source products as well as commercial products which require detailed
auditing. The nice thing is, that if you are using any Bitsmiths products down the line, then you already have a
working auditing solution within your project that is ready to go.

**Note** that we package the generated Mettle code in this package, which means that the Mettle version required in this module is important.

## Tables & Setup ##

*Audit* is designed to use a relational database with a schema/namespace of `audit`. You will need to create this database schema yourself.
It also requires four relational database tables.

The package provides the SQL code to create these tables. There are two ways to access the table creation SQL.

1. You can run `bs-audit -g postgresql` at the command line, this will print all the SQL to `stdout`.
2. You can import the bs_audit module and get the SQL as shown below:

```python

import bs_audit

print(bs_audit.get_table_sql('postgresql'))

```

**Note!** Currently only *postgresql* SQL is added to the package. If you want us to support another database let
us know and we will put it into the development pipeline.

## Library Objects ##

These are the objects in the audit product with a short description of their intended purpose.

### Audit ###

The `Audit` class (as well as it's `AuditAsync` counter part for *async* code) is the method in which one uses
the audit product. Each time you make an insert, update, or delete to a table, you can choose to audit that table
using this class.

There are a couple of presumptions that the `Audit` object makes:

- That you are auditing an object that inherits from `mettle.io.ISerializable`. This is because audit will use the `_deserialize()` method to read the objects fields.
- That the name of the auditing object has been entered into the `audit.cfg` table.
- That you are also using the auditing object from within some kind of *AutoTransaction - see bitsmiths-lib.AutoTransaction*.

Below is an example of intended use:

- We assume the Pod object contains an instance of the `Audit` object.
- We assume the Pod object contains an instance of a database connection.
- We assume the `brec` is a mettle table record of some kind.
- We assume the user identifier has been configured in the pod, and the `Audit.cfg` table has been configured to use the `modified_by` column.

```python

import copy
from mettle.lib import AutoTransaction

def save_bank_record(self, brec: tBank):
	with AutoTransaction(self.pod.audit, self.pod) as at:
		bank_tbl = self.pod.dao.dBank(self.pod.dbcon)

		brec.modified_by = self.pod.usr_id

		if bank_tbl.try_select_one_deft(brec.id):
			orig = copy.copy(bank_tbl.rec)
			bank_tbl.update(brec)
			self.pod.audit.diff(orig, bank_tbl.rec)  # audits the difference between the original and new record
		else:
			bank_tbl.insert(brec)
			self.pod.audit.diff(None, bank_tbl.rec)  # audits a brand new record.

		at.commit()

```


### TableWatch ###

This is a simply object that is designed to check on an interval for table changes. You may want to implement to update
internal caches or something if a table has row changes. Assumes that you are using the *Audit* objects whenever you
do insert, update, or deletes to table rows else it won't know.


## Change History ##

### 2.2.0 ###

| Type | Description |
| ---- | ----------- |
| Breaking | Upgraded to use `bitsmiths-mettle` version 2.2.2 |


### 2.1.6 ###

| Type | Description |
| ---- | ----------- |
| New  | Implemented auditing auto triggers |
| New  | Using the new python fetch method from `bitsmiths-mettle` (2.1.14) |
| Breaking | Table changes and new triggers required on the database (see `version_2_1_6_upgrade.postgresql.sql` in the repo) |
| New | Implemented a new function to read audit trails easier. |

Example of audit trail query/function:

```sql

select * from audit.show_trail('{"config"}', null, '{"value"}', '2022-05-01', null, '{"U"}');

```

### 2.1.5 ###

| Type | Description |
| ---- | ----------- |
| New  | Implemented the dataclass feature from the latest mettle (2.1.13) version. |

### 2.1.4 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Fixed a regression bug in base_audit.search method that was raising SQL exceptions. |

### 2.1.3 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Forced the truncation of long column values when doing auditing. |
| Bug  | Auditing of column values now works with derived dictionary and list types. |


### 2.1.0 ###

| Type | Description |
| ---- | ----------- |
| Breaking | Rename from triceraclops to audit |
| Breaking | Moved the dao import method from util.py to the __init__.py. |
| New  | Pulled in the mettle via PYPI, updated project to cater for new changes in mettle. |
| New  | You can now read the database creation from the package, also added an entry point for this. |
