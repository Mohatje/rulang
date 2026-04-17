# Rulang grammar reference

Drop-in reference for writing rulang rules. Suitable for inclusion in an LLM system prompt.

## Rule structure

A rule is:

```
<condition> => <action> [; <action>]* [; ret <expression>]?
```

- The condition evaluates to a boolean; the actions run only if it's true.
- Actions execute left-to-right; `ret <expr>` returns immediately.
- Multiple actions are separated by `;`.

Example:

```
entity.age >= 18 => entity.is_adult = true; entity.greeting = 'welcome'
```

## Condition operators

### Comparison

- `==`  equal
- `!=`  not equal
- `<`   less than
- `>`   greater than
- `<=`  less than or equal
- `>=`  greater than or equal

### Logical

- `and`
- `or`
- `not`

Precedence (lowest to highest): `or`, `and`, `not`, comparison operators. Use parentheses to override.

### Membership

- `x in y`      — `x` is a member of `y`
- `x not in y`  — `x` is not a member of `y`

### String / list containment

- `x contains y`       — `y` appears inside `x` (substring or element)
- `x not contains y`   — negation
- `x startswith y`     — `x` starts with `y`
- `x endswith y`       — `x` ends with `y`
- `x matches y`        — regex match against pattern `y`
- `x contains_any y`   — `x` contains at least one element of `y`
- `x contains_all y`   — `x` contains every element of `y`

### Existence

- `x exists`    — `x` is not null
- `x is_empty`  — `x` is null, empty string, or empty collection

## Path access

Paths navigate into the entity:

```
entity.customer.address.city
entity.items[0].price
entity.items[-1].name
```

- Dots for fields; brackets for indices (including negatives).
- `?.` is null-safe access — returns null instead of erroring on a missing segment: `entity.customer?.address?.city`.
- `??` is null coalescing: `entity.nickname ?? entity.name`.

## Literals

- **Integers**: `42`, `-3`
- **Floats**: `3.14`, `-0.5`
- **Strings**: `'hello'` or `"hello"` — single or double quoted; escapes `\n`, `\t`, `\'`, `\"`, `\\`
- **Booleans**: `true`, `false`
- **Null**: `none` (aliases: `null`)
- **Lists**: `[1, 2, 3]`, `['a', 'b']`, `[entity.x, 1]`

## Built-in functions

### Strings

- `lower(x)`  — lowercase
- `upper(x)`  — uppercase
- `trim(x)`   — strip leading/trailing whitespace (alias: `strip`)

### Collections

- `len(x)`    — length of a string / list / map / set
- `first(x)`  — first element of a list, or null
- `last(x)`   — last element of a list, or null
- `keys(x)`   — keys of a map/object
- `values(x)` — values of a map/object

### Type coercion

- `int(x)`, `float(x)`, `str(x)`, `bool(x)`

### Math

- `abs(x)`
- `round(x)` / `round(x, n)` — banker's rounding
- `min(a, b, ...)`
- `max(a, b, ...)`

### Type checks

- `is_list(x)`, `is_string(x)`, `is_number(x)`, `is_none(x)`

## Assignment (actions)

- `entity.x = value`    — set
- `entity.x += value`   — add and set
- `entity.x -= value`   — subtract and set
- `entity.x *= value`   — multiply and set
- `entity.x /= value`   — divide and set

## Workflow calls

Call a registered workflow with string name and arguments:

```
workflow("send_email", entity.customer_email)
```

Workflows can be used as actions or, if they return a value, inside expressions:

```
workflow("score", entity.id) >= 0.5 => entity.flagged = true
```

## Worked examples

```
entity.age >= 18 => entity.is_adult = true
```

```
entity.status == 'active' and entity.balance > 0 => entity.can_order = true
```

```
entity.items contains_any ['fragile', 'hazardous'] => entity.requires_signature = true
```

```
entity.customer?.vip == true => entity.discount = 0.15; entity.priority = 'high'
```

```
len(entity.line_items) > 10 or entity.total >= 1000 => workflow("notify_sales", entity.id)
```

```
not (entity.archived == true or entity.deleted == true) => ret entity.id
```

```
entity.email matches '.+@.+\\..+' => entity.email_valid = true
```

```
entity.description ?? '' contains 'urgent' => entity.priority = 'high'
```
