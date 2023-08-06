# BITSMITHS LOCO #

*LoCo* stands for **Loquacious Correspondence**. It is the common Bitsmiths python package that we use to send out communications to
user of other systems.

The intended purpose of *LoCo* is to have a shared product that offers:

- The complete customization of messages templates to be sent to external people or systems.
- To support multiple methods of sending messages:
  - Also allow dynamic/custom pluggin modules so this can be extended from outside this library
  - We currently support sending messages to `e-mail, sms, log files (debug purposes)`.
  - Next we need to support push notifications of some kind.
- To provide a single a place to store the metrics and performance sending messages to different providers.
- To provide a *transcationable* library extension so that other products can send messages and be sure those messages are always sent.
- Finally to provide a default method of archiving messages that have been sent (batch code to speak).

This product has a dependency on:

- Mettle (`bitsmiths-mettle`)
- Bitsmiths Library (`bitsmiths-lib`)
- Bitsmiths Auditing (`bitsmiths-audit`)


**Note** that we package the generated Mettle code in this package, which means that the Mettle version required in this module is important.

## Tables & Setup ##

*Loco* is designed to use a relational database with a schema/namespace of `loco` in your database. You will need to create this schema manually.
It requires several other relational database tables.

The package provides the SQL code to create these tables. There are two ways to access the table creation SQL.

1. You can run `bs-loco -g postgresql` at the command line, this will print all the SQL to `stdout`.
2. You can import the bs_loco module and get the SQL as shown below:

```python

import bs_loco

print(bs_loco.get_table_sql('postgresql'))

```

**Note!** Currently only *postgres* SQL is added to the package. If you want us to support another database let
us know and we will put it into the development pipeline.

### Table Configuration ###

TODO - Complete this section.

## Library Objects ##

TODO - Complete this section

## Change History ##

### 2.2.0 ###

| Type | Description |
| ---- | ----------- |
| Breaking | Upgraded to use `bitsmiths-mettle` version 2.2.2 |

### 2.1.9 ###

| Type | Description |
| ---- | ----------- |
| New  | Using the new bitsmiths-audit (2.1.6) version that has auto triggers. |
| New  | Using the new python fetch method from bitsmiths-mettle (2.1.14) |

### 2.1.8 ###

| Type | Description |
| ---- | ----------- |
| New  | Implemented the dataclass feature from the latest mettle (2.1.13) version. |


### 2.1.7 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Applied code generation bug fix from lastest mettle library. |

### 2.1.6 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Improved the regex email in the base loco object to allow for email addresses with single quotes. |

### 2.1.5 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Fixed the template updown batch to use the correct import from the refactored mettle change. |

### 2.1.4 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Fixed the SMTP Provider that was still using legacy imports and bs_lib methods. |

### 2.1.3 ###

| Type | Description |
| ---- | ----------- |
| Bug  | Fixed the dynamic importing of provider and correspondence types. |
| Bug  | Fixed the json.dumps and json.loads errors caused by the mettle upgrade. |


### 2.1.0 ###

| Type | Description |
| ---- | ----------- |
| New  | Pulled in the mettle via PYPI, updated project to cater for new changes in mettle. |
| New  | You can now read the database creation from the package, also added an entry point for this. |
| New  | You can change or add new correspondence providers with the environment variable 'BITSMITHS_LOCO_CUST_PROVIDERS' |
