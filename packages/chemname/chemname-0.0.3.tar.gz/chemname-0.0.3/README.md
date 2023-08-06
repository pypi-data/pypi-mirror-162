# Chemname

This package converts any eligible text to its equivalent using chemical element names.

## Usage

```
>>> from chemname import chem
```

Results are return as a list of lists, each containing a possible alternative. If there is one possiblity:

```
>>> chem.chemname("Ash")
    [['As', 'H']]
```

The matching process is case insensitive.

```
>>> chem.chemname("ash")
    [['As', 'H']]
```

If there are more possibilities:

```
>>> chem.chemname("Practice")
    [['P', 'Ra', 'C', 'Ti', 'Ce'], ['Pr', 'Ac', 'Ti', 'Ce']]
```