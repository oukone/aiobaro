---
name: Matrix spec template
about: This template provides a guideline on how to create issues related to matrix
  client-server spec implementation
title: 'Matrix client implementation: ex. [createRoom]'
labels: Matrix spec, enhancement
assignees: ''

---

-  [Matrix Spec reference](https://matrix.org/docs/spec/client_server/r0.6.1#post-matrix-client-r0-createroom)

POST /_matrix/client/r0/createRoom  HTTP/1.1
Content-Type: application/json

```json
{
    "preset": "public_chat",
    "room_alias_name": "thepub",
    "name": "The Grand Duke Pub",
    "topic": "All about happy hour",
    "creation_content": {
        "m.federate": false
    }
}
```

&nbsp;

## Request format

Parameter | Type | Description
-- | -- | --
**Path Parameters**
param1 | string | Required. param description.
**Query Parameters**
param1 | string | Required. param description.
**Json**
field1 | string | Required. field description.

&nbsp;

## Response format
Field | Type | Description
-- | -- | --
**Json**
field1 | string | Required. field description.

&nbsp;
&nbsp;

Rate-limited:	No.
Requires auth:	Yes.
