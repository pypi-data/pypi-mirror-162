# -*- coding: utf-8 -*-
CHANGE_SPECIFIED_IN_BODY = 'No attributes to change specified in body'

DDE_REBOOT_MSG = 'The DDE must be rebooted for netcfg changes to take effect. Please send a request to reboot.'
NO_REBOOT_REQUIRED = 'No reboot is required to apply these changes. Your new settings will take effect immediately.'
DDE_REBOOTING_MSG = 'The DDE will be rebooted in {}s.'
REBOOTING_SYSTEM = 'Going to reboot the system'
REBOOTING_TIME_WARNING = 'Going to reboot the system in {}s'
NETCFG_BACKUP = 'Netcfg has been backed up'
NETCFG_RESTORE = 'Netcfg has been restored'
DELETE_SUCCESS_MSG = 'Delete {} succeeded'
ASYNC_SUCCESS_MSG = 'Operation is running in background, check asynctask task_id:{} for progress status'

DISJOIN_WORKGROUP_SUCCESS_MSG = 'Disjoin workgroup succeeded'
DISJOIN_ADSDOMAIN_SUCCESS_MSG = 'Disjoin ads domain succeeded'

INTERFACE_FORMAT_ERROR = 'Interfaces are <alphanumeric>[.<vlanid>]:<interface_number>, where vlanid is optional.'

NOT_FOUND = 'NOT FOUND'

paginated_params_desc = {
    'name':
        {'in': 'path',
         'description': 'name (device name, interface name, ip address etc.) of requested item',
         'type': 'string',
         'required': True},
    'page_size':
        {'in': 'query',
         'description': 'Requested amount of items per page',
         'type': 'integer',
         'minimum': 1,
         'required': False},
    'page':
        {'in': 'query',
         'description': 'Requested output page',
         'type': 'integer',
         'minimum': 1,
         'required': False}
}

# Note that each entry here corresponds to a @doc(tags='...') on a view entity.
TAGS = [
    dict(name='Asynctasks', description='This section provides all the operations to list and act on async tasks.'),
    dict(name='DDE Nodes', description='This section provides all the operations to list and act on DDE nodes.'),
    dict(name='Events', description='This section provides all events-related operations.'),
    dict(name='Health State', description='This section provides all the operations to receive health information.'),
    dict(name='Management Users', description='This section provides all the operations to list and act on management users.'),
    dict(name='NAS App Specific Shares', description='This section provides all the operations to list and act on application specific shares.'),
    dict(name='NAS CIFS ADS Domains', description='This section provides all the operations to list and act on CIFS ADS Domains.'),
    dict(name='NAS CIFS Shareadmins', description='This section provides all the operations to list and act on CIFS Shareadmins.'),
    dict(name='NAS CIFS SMB Settings', description='This section provides all the operations to list and act on CIFS SMB Settings.'),
    dict(name='NAS CIFS Workgroups', description='This section provides all the operations to list and act on CIFS Workgroups.'),
    dict(name='NAS CIFS Shares', description='This section provides all the operations to list and act on CIFS shares.'),
    dict(name='NAS NFS Settings', description='This section provides all the operations to list and act on NFS Settings.'),
    dict(name='NAS NFS Shares', description='This section provides all the operations to list and act on NFS shares.'),
    dict(name='NAS Shares', description='This section provides all the operations to list and act on generic nas shares(all protocols).'),
    dict(name='Network Bond Interfaces', description='This section provides all the operations to list and act on network bond interfaces.'),
    dict(name='Network Devices', description='This section provides all the operations to list and act on network devices.'),
    dict(name='Network Hosts', description='This section provides all the operations to list and act on network hosts.'),
    dict(name='Network Interfaces', description='This section provides all the operations to list and act on network interfaces.'),
    dict(name='OST AIRs', description='This section provides all operations related to OST AIRs.'),
    dict(name='OST Replication', description='This section provides all operations related to OST replication.'),
    dict(name='OST Settings', description='This section provides all the operations to list and act on OST settings.'),
    dict(name='OST Storage Servers', description='This section provides all the operations to list and act on OST storage servers.'),
    dict(name='Racks', description='This section provides all the operations to list and act on rack, enclosures and drives.'),
    dict(name='Static Routes', description='This section provides all the operations to list and act on network static routes.'),
    dict(name='System Configuration', description='This section provides all system configuration-related operations.'),
    dict(name='Users', description='This section provides all the operations to list and act on users.'),
    dict(name='VTL Drives', description='This section provides operation to list VTL drives.'),
    dict(name='VTL Hosts', description='This section provides all the operations to list and act on VTL host.'),
    dict(name='VTL Libraries', description='This section provides operation to list VTL libraries.'),
    dict(name='VTL Partitions & Media & Hostmapping', description='This section provides all the operations to list and act on VTL partitions, media, hostmapping.'),
    dict(name='VTL Targets', description='This section provides operation to list VTL targets.'),
    dict(name='DDE Network Tools', description='This section provides DDE network tools operations'),
]

API_DESCRIPTION = '''
INFINIDAT InfiniGuard API provides programmatic access to the InfiniGuard system. Use the APIs to access the system components and entities, create and edit entities and perform storage operations.

This document is an addendum to the InfiniGuard User Guide, and only documents the InfiniGuard API. It does not provide details for high level workflow or the pre-requisites for each command.

## Terminology

* InfiniGuard - The INFINIDAT  system that is queried and posted to through the InfiniGuard API.
* Entity - A logical entity, representing a portion or component of the InfiniGuard business logic.
* Object - In REST terminology, the InfiniGuard entity is an Object, a data structure with a known set of fields. The RESTful API request operates on, or returns the data of an object. For the data structure of an object – see the next section.
* Collection - An array of entities that is requested by an API request, along with possible support for filtering, sorting, field selection, pagination, and other common functions. For example, all of the users on an InfiniGuard system, some of the users of an InfiniGuard system that meet a certain criteria. For the data structure of a collection – see the next section.
All the resources and methods mentioned here are public; that is, are available for the use by end-users.

## Request headers

The client sends the InfiniGuard a request with the following headers:

* Content-Type: application/json
# Protocol Basics

This section covers the structure of the supported requests, and their repsonses. We'll start from the response.

## Data structure

The API uses the JSON protocol. The JSON protocol comprises the following data types:

* Null - null (only one value)
* Boolean - true or false
* Number - Numeric values, e.g: 123456
* String - Characters, enclosed in quotes, e.g: "some text"
* Object - A JSON object is a container of fields and values. Objects may contain nested objects. For example:
```
{
"age": 42,
"name": "Joe",
"is_married": true,
"children_ids": [2, 5, 4],
"job_id": null,
"metadata": {
           "religion": "PASTAFARIANISM",
           "political_affiliation": null
          }
}
```  
    
## CRUD operations

(CRUD - Create-Read-Update-Delete)

The following HTTP methods create, read, update and delete InfiniGuard objects and collections. For example:

|Operation           |Syntax                  |Body structure  |Response structure          |
|--------------------|------------------------|----------------|----------------------------|
|Create an entity    |POST /collection        |Required        |The created entity          |
|Read an entity      |GET /collection/<id>    |                |The read entity             |
|Read all entities   |GET /collection         |                |A paginated list of entities|
|Update an entity    |PATCH /collection/<id>  |Required        |The updated entity          |
|Delete an entity    |DELETE /collection/<id> |                |The deleted entity          |


## Response to a request

Each response returns a JSON-encoded object in the HTTP body, which contains 3 attributes:

* result - the actual data returned by the request. May be null in case of error, or if the data is not available yet.
* metadata - additional information about the result, such as the pagination data and so on.
* error - in case of an error, contains the error code and human-readable error message. Otherwise it is null.
### Successful request

A response to a request that ended successfully contains the following:

* The result part returns data (in this case: role, email and uid of two users).
* The metadata returns details about the result:
** ready means that the request ended successfully and a new request can be sent.
** The other metadata provides details about the number of objects that were returned, and the way the result is paginated
* The error part returns null, as the request ended successfully.

```
{
    "result": [
        {
            "role": "ADMIN",
            "email": "alice@example.com",
            "uid": "alicia"
        },
        {
            "role": "ADMIN",
            "email": "bob@example.com",
            "uid": "bob"
        }
    ],
    "metadata": {
        "ready": true,
        "number_of_objects": 2,
        "page_size": 50
        "pages_total": 1,
        "page": 1,
    },
    "error": null
}
```

## A request that ends with an error

Here is a sample response from a request that ended with an error:

* The result part returns null, as the request was not answered.
* The metadata part returns the following details about the result:
** ready means that the request ended successfully and a new request can be sent.
** No information about returned objects, as no objects were returned.

```
{
    "result": null,
    "metadata": {
        "ready": true
    },
    "error": {
        "message": "You must authenticate",
        "code": "AUTHENTICATION_REQUIRED"
    },
}
```

## Authentication

All API requests must be accompanied by an Authorization header containing a Base64-encoded username:password pair (HTTP basic authentication). Otherwise, an HTTP 401 error is returned.

The only exception is the login request, which purpose is to check whether a given username and password pair is valid.

## The structure of the collection

When requesting a collection of objects (for example, all users for a system), the result can span over hundreds of objects and thousands of lines. In order to enhance its readability, the following response attributes can be set as part of the GET request:

* Pagination - how many objects are displayed on each page
* Filter - which of the collection object will be displayed in the response
* Sort - how the objects are sorted
* Fields - which of the object fields is included in the response
## Pagination

For ease of readability, the objects that the response returns are paginated. The default pagination is 50 objects per page.

You can change the pagination by specifying two parameters:

* page_size - The number of entities on each page.
* page - The number of the page that is displayed on screen.

Example 1: default pagination of GET api/rest/volumes

|Request|Result|
|-------|------|
|GET request |api/rest/volumes|

Response

```
{
    "result": [
        {
            "id": 1,
            "name": "vol-01",
            ... ... ...
        },
        {
            "id": 2,
            "name": "vol-02",
            ... ... ...
        },
        ... ... ...
}
```

Metadata

```    
"metadata": {
        "ready": true,
        "page": 1,
        "number_of_objects": 15,
        "page_size": 50,
        "pages_total": 1
    }
```    

|Field   |Result|
|--------|------|
|Page    |As there are 15 objects in the response, and the size of a page is 50 objects, there is only once page.|
|Number of objects   |The number of objects in the collections. This number is not affected by the pagination.|
|Page size   |50 objects per page.|

Example 2: 3 volumes per page, displaying the second page

|Field   |Result|
|--------|------|
|GET request |api/rest/volumes?page_size=3&page=2|
|Response    |As there are 3 volumes per page, the 2nd page displays the 4th, 5th and 6th volumes.|


```
{
    "result": [
        {
            "id": 4,
            "name": "vol-04",
            ... ... ...
        },
        {
            "id": 5,
            "name": "vol-05",
            ... ... ...
        },
        {
            "id": 6,
            "name": "vol-06",
            ... ... ...
        },
        ... ... ...
}
```

Metadata   

``` 
"metadata": {
        "ready": true,
        "page": 2,
        "number_of_objects": 15,
        "page_size": 3,
        "pages_total": 5
    }
```   

|Field   |Result|
|--------|------| 
|Page    |As requested, this response includes page 2.|
|Number of objects   |The number of objects in the collections. This number is not affected by the pagination.|
|Page size   |As requested, there are 3 objects per page.|

## Filtering

Some responses can be filtered, so that only specific objects will be returned. For such responses, you can filter the returned objects by stating a valid value to one of their attributes.

### Simple filtering example

Setting a filter is done by specifying the filter argument (attribute and value). In the following example, only first node events are returned.

```
api/rest/events/code?source_node_id=1
```

If the field and values are set incorrectly, the following error messages are returned:

* ATTRIBUTE_NOT_FOUND - The attributes could not be found. Resolve this error by making sure that the attribute indeed exists for this entity. For example, that the volume does have a type attribute.
* MALFORMED_PARAMETER - The value of the attribute is illegal. Resolve this problem by making sure that the attribute you filter the response with, is legal. For example, that type accepts master.

You can use the following operators in order to filter the response:

|Operator    |Acceptable value    |Examples|
|------------|--------------------|--------|
|eq  |number/string   |api/rest/events?event_id=eq:134|
|neq |number/string   |api/rest/events?visibility=neq:customer|
|is  |null    |To find all volumes that are not members of a consistency group (that is, whose cg_id value is null), use: api/rest/volumes?cg_id=is:null|
|isnot   |null    |To find all volumes that are members of any consistency group (that is, whose cg_id value is not null), use:api/rest/volumes?cg_id=isnot:null|
|lt  |number/string   |api/rest/events?timestamp=lt:2000000000000|
|leq |number/string   |api/rest/events?event_id=leq:646|
|gt  |number/string   |api/rest/events?event_id=gt:646|
|geq |number/string   |api/rest/events?timestamp=geq:2000000000000|
|in  |list    |Input list is val1, val2,.. which can be enclosed with () or [] or not enclosed at all.|
|notin   |list    |Input list is val1, val2,.. which can be enclosed with () or [] or not enclosed at all.|
|between |list    |A list of exactly two items, e.g. [5,10]; the filter is inclusive, equivalent to x >= 5 AND y <= 10.|
|like    |string  |Searches for a field containing the value (case-insensitive). "like:ny" on {MEENY, MINY, MOE, nyc} returns {MEENY, MINY, nyc}|

Notes:

* When filtering on more than one field, the conditions are joined.
* Unless otherwise stated, string comparisons are case insensitive.

## Sorting

For most of the available collections, the objects can be sorted by one or more fields. The sorting is done according to order of the fields (from left to right). The syntax for sorting is as follows:

```
api/rest/collection?sort=<field name>[,<field name>]
```

The default sorting order is ascending. To specify a descending order, add a minus sign (-) before the field name. For example:

```
/api/rest/events?sort=-level,timestamp
```

The specific fields that can be used depend on the objects in question. Please refer to the documentation of each request for the list of valid fields.

## Choosing Which Fields to Get

By default, requests that return objects will return all the fields of each object. If you are interested in only a few fields from the object, you can use the fields query parameter in order to "pluck" them from the objects and omit all other fields. This parameter should contain a comma-separated list of field names. For example:

```
GET /api/rest/events?fields=id,uuid
```

The response:

```
{
    "error": null,
    "result": [
        {
            "id": 1,
            "uuid": "a469575e-acd9-435f-bc5f-79ada0bc6add"
        },
        {
            "id": 2,
            "uuid": "326be807-6550-472a-9c68-b03f4b5171fa"
        },
        {
            "id": 3,
            "uuid": "799355fe-c529-4482-a2cc-ab672dffc6d5"
        },
        ...
    ],
    "metadata": {
        ...
    }
}
```

The fields query parameter is supported by all API methods that are tagged as "pluckable".

Note that passing a non-existent field name is not an error; it simply won't be returned for any object that doesn't have such a field.



## List of API Error Codes

Successful GET request

|Response|Code|Result|
|--------|----|------|
|OK      |200 |      |

Successful post request

|Response|Code|Result|
|--------|----|------|
|Created |201 |The response contains the created object.|

Request error

|Response|Code|Result|
|--------|----|------|
|UNKNOWN_PARAMETER   |400 |The request contains a parameter that is not part of the collection / object.|
|MALFORMED_PARAMETER |400 |The value of the parameter is invalid.|
|MALFORMED_CONTENT   |400 |The request contains wrong content.|
|MALFORMED_REQUEST   |400 |The request contains wrong headers.|
|WRONG_PARAMETER |400 |The request contains a parameter is not part of the collection / object.|
|MISSING_QUERY_PARAMETER |400 |A manadatory parameter is missing from the request.|
|MISSING_FIELD   |400 |A manadatory parameter is missing from the request.|
|MISSING_CONTENT |400 |The request contains insufficient information for responding.|
|UNSUPPORTED_FIELD   |400 |The resource or service cannot accept a specified field or property|
|MAX_PAGE_SIZE_VIOLATION |400 |The requested page_size is too large (>1000)|
|NOT_FOUND   |404 |Object not found.|
|UNKNOWN_PATH    |404 |Requsted service does not exist.|
|CONFLICT    |409 |The request conflicts with already existing collections (for example when trying to create an object that already exists).|

Approval required

|Response|Code|Result|
|--------|----|------|
|APPROVAL_REQUIRED   |403 |The operation requires a specific user-approval.|

Authentication erros

|Response|Code|Result|
|--------|----|------|
|AUTHENTICATION_REQUIRED |401 |The authentication headers are missing or invalid.|
|UNAUTHORIZED    |403 |The user is not authorized to perform the requested action.|

Other erros

|Response|Code|Result|
|--------|----|------|
|RECONFIGURING    |307    |The system is currently reconfiguring, and cannot respond temporarily. Request should be retried in a few seconds.|
|ILLEGAL_NODE_STATE   |409    |The requested node is not the master node.|
|OPERATION_DENIED_CLUSTER_NOT_FULL    |409    |Cluster is not full or node in joining state.|
|NOT_SUPPORTED_IN_SYSTEM_STATE    |409    |The request is not valid for the current system state.|
|INTERNAL_SERVER_ERROR    |500    |Internal server error.|

Refer to the documentation of specific API methods for information about additional error codes that they may return.
## Example workflows

### OST device workflow

The following workflow describes the process of configuring a DDE node and defining OST storage server and LSU.

The first steps (related to networking and NetBoost configuration) only need to be performed once. Other steps can be repeated as needed for each additional OST server and/or LSU.

### Configure host networking

Configure DNS, gateway and hostname of the DDE node

Request path

```
POST  /api/dde/1/api/network/host/
```

Request body

```
  {
    "default_gateway" : "10.10.10.1",
    "dns_servers" : [ "8.8.8.8", "8.8.8.4" ],
    "hostname" : "host0",
    "search_domain" : [ "localhost", "blah.net" ]
  } 
```

Response

```
  {
    "message" : "Reboot the DDE for the command to be applied.",
    "metadata" : {
      "number_of_objects" : 1,
      "page" : 1,
      "page_size" : 50,
      "pages_total" : 1
    },
    "result" : {
      "default_gateway" : "10.10.10.1",
      "dns_servers" : [ "8.8.8.8", "8.8.8.4" ],
      "hostname" : "host0",
      "search_domain" : [ "localhost", "blah.net" ]
    } 
  } 
```  

### Configure bond device and IP

Configure the bond interface and IP address

Request path

```
POST /api/dde/1/api/network/bonds/
```

Request body

```
{
    "default_gateway" : "YES",
    "ext_host_ip" : "YES",
    "gateway" : "10.10.10.1",
    "intfname" : "dev0.2:1",
    "ip_address" : "10.10.10.10",
    "mode" : "lacp",
    "mtu" : 1500,
    "nat" : "string",
    "netmask" : "255.255.255.0",
    "segments" : "ALL",
    "slave_names" : [ "p5p1", "p5p2" ]
} 
```

Response

```
{
    "message" : "Reboot the DDE for the command to be applied.",
    "metadata" : {
      "number_of_objects" : 1,
      "page" : 1,
      "page_size" : 50,
      "pages_total" : 1
    },
    "result" : {
      "configured" : true,
      "devname" : "bond0",
      "mtu" : 1500,
      "options" : "mode=4",
      "slave_names" : [ "p5p1", "p5p2" ],
      "type" : "Bond"
    } 
} 
```

### Reboot

Reboot the DDE node in order to apply network settings. Wait until the node finishes the reboot process.

Request path

```
POST /api/dde/1/api/node/reboot
```

Request body

```
{
    "wait_time" : 20
}
```

Response

```
{
    "message" : "Reboot the DDE for the command to be applied."
} 
```

### Enable NetBoost

Enable NetBoost host side plugin deduplication option

Request path

```
PATCH /api/dde/1/api/ost/ostsettings
```

Request body

```
{
    "encryption" : "on",
    "encryptiontype" : "aes256",
    "netboost" : "on"
}
```

Response

```
{
    "metadata" : {
      "number_of_objects" : 1,
      "page" : 1,
      "page_size" : 50,
      "pages_total" : 1
    },
    "result" : {
      "encryption" : true,
      "encryption_type" : "aes256",
      "netboost" : true,
      "netboost_enabled_first_time" : true
    } 
}
```

### Create OST User

Create the user used for OST access from backup software

Request path

```
POST /api/dde/1/api/user/
```

Request body

```
{
    "description" : "User Description",
    "name" : "ost",
    "password" : "password",
    "role" : "backupuser"
} 
```
  
Response

```
{
    "metadata" : {
      "number_of_objects" : 1,
      "page" : 1,
      "page_size" : 50,
      "pages_total" : 1
    },
    "result" : {
      "description" : "User Description",
      "name" : "ost",
      "role" : "backupuser"
    } 
}
```
  
### Create OST server

Create the OST server

Request path

```
POST /api/dde/1/api/ost/storage_servers/
```

Request body

```
{
    "desc" : "server1 description",
    "maxconnect" : 200,
    "name" : "server1"
}
```
  

Response

```
{
    "metadata" : {
      "number_of_objects" : 1,
      "page" : 1,
      "page_size" : 50,
      "pages_total" : 1
    },
    "result" : {
      "active_connections" : 0,
      "allowed_replication_targets" : [ ],
      "backup_images" : 0,
      "concurrentopdup" : false,
      "desc" : "server1 description",
      "lsu_count" : 0,
      "maxconnect" : 200,
      "name" : "server1"
    }
}
```

### Create LSU

Create LSU inside the OST server

Request path

```
POST  /api/dde/1/api/ost/storage_servers/server1/lsus/
```

Request body

```
{
    "capacity" : 200,
    "desc" : "lsu1 on server1",
    "name" : "lsu1"
}
```

Response

```
{
    "metadata" : {
      "number_of_objects" : 1,
      "page" : 1,
      "page_size" : 50,
      "pages_total" : 1
    },
    "result" : {
      "air_user" : "ost",
      "backup_images" : 0,
      "desc" : "lsu1 on server1",
      "lsu_name" : "lsu1",
      "ost_air" : false,
      "physical_capacity" : 200,
      "server_name" : "server1",
      "target_host_id" : "",
      "target_lsu_name" : "",
      "target_server_name" : ""
    }   
}
```
  
'''
