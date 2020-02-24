# test



## API

### /pets

#### GET

get all pets

##### Responses

|Status|Description|
|---|---|
|200|OK|
##### Response Schema

Status Code 200

|Field|Type|Required|Description|
|---|---|---|---|
|name|string|False|pet name|
##### Response Example

200 Response

```json
{
    "name": "string"
}
```
#### POST

##### Request Body

Body Parameter

|Field|Type|Required|Description|
|---|---|---|---|
|id|string|False||
|name|string|False||
Body Example

```json
{
    "id": "string",
    "name": "string"
}
```
##### Responses

|Status|Description|
|---|---|
|200|OK|
##### Response Schema

Status Code 200

|Field|Type|Required|Description|
|---|---|---|---|
##### Response Example

200 Response

```json
"string"
```
#### PUT

##### Responses

|Status|Description|
|---|---|
|200|OK|
##### Response Schema

Status Code 200

|Field|Type|Required|Description|
|---|---|---|---|
|name|string|False||
##### Response Example

200 Response

```json
{
    "name": "string"
}
```
## Schemas

### test

**Properties**

|Field|Type|Required|Description|
|---|---|---|
|id|string|False||
|object1|object|False||
|»name|string|False||
|array1|[string]|False||
|array2|[object]|False||
|»array2_o1|string|False||
|t1|object|False||
|»id|string|False||
|»name|string|False||
**Example**

```json
{
    "id": "string",
    "object1": {
        "name": "string"
    },
    "array1": [
        "string"
    ],
    "array2": [
        {
            "array2_o1": "string"
        }
    ],
    "t1": {
        "id": "string",
        "name": "string"
    }
}
```
### t1

**Properties**

|Field|Type|Required|Description|
|---|---|---|
|id|string|False||
|name|string|False||
**Example**

```json
{
    "id": "string",
    "name": "string"
}
```
### t2

hehe

**Properties**

|Field|Type|Required|Description|
|---|---|---|
|t2|string|False|hehe|
**Example**

```json
{}
```
